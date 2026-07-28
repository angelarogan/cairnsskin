# Compliance checklist — pre-publication review

Complete for every piece of health/treatment content before setting
`draft: false` and `reviewStatus: "published"`. This is a working
checklist, not legal advice — when in doubt, get sign-off from someone
qualified to assess AHPRA advertising compliance.

## Claims

- [ ] No guaranteed results or "everyone will see X" language
- [ ] No unsupported superiority claims over other treatments/providers
- [ ] No misleading comparisons
- [ ] No fear-based or alarmist language
- [ ] No claims presented as settled fact where evidence is limited or emerging
- [ ] No encouragement of unnecessary treatment
- [ ] No cosmetic injectable or prescription-medicine promotion
- [ ] Before/after content only included after separate compliance review
- [ ] No testimonials unless separately cleared for advertising compliance

## Balance

- [ ] Benefits and limitations both discussed
- [ ] Possible side effects covered where relevant
- [ ] Downtime and suitability addressed
- [ ] Contraindications mentioned where known
- [ ] Variability of outcomes acknowledged
- [ ] Suggests consultation where individual assessment matters

## Terminology

- [ ] Treatment name matches `src/data/treatments.ts` exactly
- [ ] Treatment's `verified` flag is `true` (or flagged for follow-up
      if publishing before verification is complete)
- [ ] Not implying every Laser Clinics location offers this treatment

## Sourcing

- [ ] All sources listed are real and checkable
- [ ] Manufacturer claims are labelled as such, distinct from
      independent research
- [ ] No invented statistics, studies or credentials

## Frontmatter

- [ ] `reviewStatus` reflects actual review stage
- [ ] `reviewedBy` set once clinically reviewed
- [ ] `reviewDate` / `updatedDate` current
- [ ] `ahpraRisk` set honestly (`low` / `moderate` / `high`)
- [ ] `clinicVerificationRequired` left `true` until Laser Clinics
      Cairns specifics are confirmed

## Sign-off

- [ ] Clinical reviewer named
- [ ] Compliance reviewer named
- [ ] Final `draft: false` change made only after both sign-offs
