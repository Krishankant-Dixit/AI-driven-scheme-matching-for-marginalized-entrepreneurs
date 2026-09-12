import { useState } from "react";
import { Link } from "react-router-dom";

import { apiClient } from "../services/api";

const initialForm = {
  name: "",
  age: "",
  gender: "",
  category: "",
  state: "",
  district: "",
  rural_urban: "",
  business_name: "",
  business_type: "",
  business_sector: "",
  business_stage: "",
  business_description: "",
  annual_income: "",
  investment_capacity: "",
  loan_required: "",
  education: "",
  disability_status: "",
  social_category_details: "",
  existing_business_duration: "",
  number_of_employees: "",
};

const options = {
  gender: ["MALE", "FEMALE", "OTHER", "PREFER_NOT_TO_SAY", "UNKNOWN"],
  category: ["GENERAL", "SC", "ST", "OBC", "MINORITY", "WOMEN", "OTHER", "UNKNOWN"],
  rural_urban: ["RURAL", "URBAN", "UNKNOWN"],
  business_type: ["PROPRIETORSHIP", "PARTNERSHIP", "COMPANY", "SELF_HELP_GROUP", "INDIVIDUAL", "OTHER", "UNKNOWN"],
  business_sector: ["AGRICULTURE", "FOOD_PROCESSING", "MANUFACTURING", "SERVICES", "RETAIL", "HANDICRAFT", "TEXTILE", "TECHNOLOGY", "EDUCATION", "HEALTHCARE", "TOURISM", "TRANSPORT", "OTHER", "UNKNOWN"],
  business_stage: ["IDEA", "NEW", "EXISTING", "EXPANSION", "UNKNOWN"],
};

function humanize(value) {
  return value.replaceAll("_", " ");
}

function validate(form) {
  const errors = {};
  ["name", "state", "district"].forEach((field) => {
    if (!form[field].trim()) errors[field] = "This field is required.";
  });

  if (form.age !== "" && (!/^\d+$/.test(form.age) || Number(form.age) < 1 || Number(form.age) > 120)) {
    errors.age = "Enter an age between 1 and 120.";
  }

  ["annual_income", "investment_capacity", "loan_required", "existing_business_duration", "number_of_employees"].forEach((field) => {
    if (form[field] !== "" && (!/^\d+(\.\d+)?$/.test(form[field]) || Number(form[field]) < 0)) {
      errors[field] = "Enter a zero or positive number.";
    }
  });
  return errors;
}

function toNullableNumber(value) {
  return value === "" ? null : Number(value);
}

function Section({ title, children }) {
  return (
    <section className="form-section">
      <h2>{title}</h2>
      <div className="form-grid">{children}</div>
    </section>
  );
}

function Field({ name, label, required, error, children }) {
  return (
    <label className="form-field" htmlFor={name}>
      <span>
        {label} {required && <em>Required</em>}
      </span>
      {children}
      {error && <small className="field-error">{error}</small>}
    </label>
  );
}

export default function ProfileForm() {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState({ type: "", message: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setErrors((current) => ({ ...current, [name]: undefined }));
    setStatus({ type: "", message: "" });
  }

  async function submitForm(event) {
    event.preventDefault();
    const nextErrors = validate(form);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length) {
      setStatus({ type: "error", message: "Please correct the highlighted fields." });
      return;
    }

    const payload = Object.fromEntries(
      Object.entries(form).map(([key, value]) => [
        key,
        ["age", "annual_income", "investment_capacity", "loan_required", "existing_business_duration", "number_of_employees"].includes(key)
          ? toNullableNumber(value)
          : value.trim() || null,
      ]),
    );

    setIsSubmitting(true);
    setStatus({ type: "", message: "" });
    try {
      const response = await apiClient.post("/api/profile", payload);
      window.localStorage.setItem("sih26092_profile_id", response.data.profile_id);
      setStatus({ type: "success", message: `Profile saved. ID: ${response.data.profile_id}` });
    } catch (error) {
      const detail = error.response?.data?.detail;
      setStatus({ type: "error", message: typeof detail === "string" ? detail : "Unable to save the profile. Please try again." });
    } finally {
      setIsSubmitting(false);
    }
  }

  function resetForm() {
    setForm(initialForm);
    setErrors({});
    setStatus({ type: "", message: "" });
  }

  return (
    <form className="profile-form" onSubmit={submitForm} noValidate>
      <Section title="Personal Information">
        <Field name="name" label="Name" required error={errors.name}>
          <input id="name" name="name" value={form.name} onChange={updateField} placeholder="Your full name" />
        </Field>
        <Field name="age" label="Age" error={errors.age}>
          <input id="age" name="age" type="number" min="1" max="120" value={form.age} onChange={updateField} placeholder="Optional" />
        </Field>
        <Field name="gender" label="Gender">
          <select id="gender" name="gender" value={form.gender} onChange={updateField}>
            <option value="">Not provided</option>
            {options.gender.map((value) => <option key={value} value={value}>{humanize(value)}</option>)}
          </select>
        </Field>
        <Field name="category" label="Category">
          <select id="category" name="category" value={form.category} onChange={updateField}>
            <option value="">Not provided</option>
            {options.category.map((value) => <option key={value} value={value}>{humanize(value)}</option>)}
          </select>
        </Field>
      </Section>

      <Section title="Location">
        <Field name="state" label="State" required error={errors.state}>
          <input id="state" name="state" value={form.state} onChange={updateField} placeholder="Your state" />
        </Field>
        <Field name="district" label="District" required error={errors.district}>
          <input id="district" name="district" value={form.district} onChange={updateField} placeholder="Your district" />
        </Field>
        <Field name="rural_urban" label="Location type">
          <select id="rural_urban" name="rural_urban" value={form.rural_urban} onChange={updateField}>
            <option value="">Not provided</option>
            {options.rural_urban.map((value) => <option key={value} value={value}>{humanize(value)}</option>)}
          </select>
        </Field>
      </Section>

      <Section title="Business Information">
        <Field name="business_name" label="Business name">
          <input id="business_name" name="business_name" value={form.business_name} onChange={updateField} placeholder="Optional business name" />
        </Field>
        <Field name="business_type" label="Business type">
          <select id="business_type" name="business_type" value={form.business_type} onChange={updateField}>
            <option value="">Not provided</option>
            {options.business_type.map((value) => <option key={value} value={value}>{humanize(value)}</option>)}
          </select>
        </Field>
        <Field name="business_sector" label="Business sector">
          <select id="business_sector" name="business_sector" value={form.business_sector} onChange={updateField}>
            <option value="">Not provided</option>
            {options.business_sector.map((value) => <option key={value} value={value}>{humanize(value)}</option>)}
          </select>
        </Field>
        <Field name="business_stage" label="Business stage">
          <select id="business_stage" name="business_stage" value={form.business_stage} onChange={updateField}>
            <option value="">Not provided</option>
            {options.business_stage.map((value) => <option key={value} value={value}>{humanize(value)}</option>)}
          </select>
        </Field>
        <Field name="business_description" label="Business description">
          <textarea id="business_description" name="business_description" value={form.business_description} onChange={updateField} placeholder="Tell us briefly about the business" rows="4" />
        </Field>
      </Section>

      <Section title="Financial Information">
        <Field name="annual_income" label="Annual income">
          <input id="annual_income" name="annual_income" type="number" min="0" value={form.annual_income} onChange={updateField} placeholder="Optional amount in INR" />
        </Field>
        <Field name="investment_capacity" label="Investment capacity">
          <input id="investment_capacity" name="investment_capacity" type="number" min="0" value={form.investment_capacity} onChange={updateField} placeholder="Optional amount in INR" />
        </Field>
        <Field name="loan_required" label="Loan required">
          <input id="loan_required" name="loan_required" type="number" min="0" value={form.loan_required} onChange={updateField} placeholder="Optional amount in INR" />
        </Field>
      </Section>

      <Section title="Additional Information">
        <Field name="education" label="Education">
          <input id="education" name="education" value={form.education} onChange={updateField} placeholder="Optional" />
        </Field>
        <Field name="disability_status" label="Disability status">
          <input id="disability_status" name="disability_status" value={form.disability_status} onChange={updateField} placeholder="Optional" />
        </Field>
        <Field name="social_category_details" label="Social category details">
          <input id="social_category_details" name="social_category_details" value={form.social_category_details} onChange={updateField} placeholder="Optional" />
        </Field>
        <Field name="existing_business_duration" label="Existing business duration (years)" error={errors.existing_business_duration}>
          <input id="existing_business_duration" name="existing_business_duration" type="number" min="0" step="0.1" value={form.existing_business_duration} onChange={updateField} placeholder="Optional" />
        </Field>
        <Field name="number_of_employees" label="Number of employees" error={errors.number_of_employees}>
          <input id="number_of_employees" name="number_of_employees" type="number" min="0" step="1" value={form.number_of_employees} onChange={updateField} placeholder="Optional" />
        </Field>
      </Section>

      {status.message && <p className={`form-status ${status.type}`}>{status.message}{status.type === "success" && <Link className="status-link" to="/recommendations">View recommendations</Link>}</p>}
      <div className="form-actions">
        <button className="primary-button" type="submit" disabled={isSubmitting}>{isSubmitting ? "Saving..." : "Save profile"}</button>
        <button className="secondary-button" type="button" onClick={resetForm} disabled={isSubmitting}>Reset</button>
      </div>
    </form>
  );
}