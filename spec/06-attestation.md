# 06 — Attestation

Binding a record to its producer with a signature.

## 6.1 The attestation object

**ATT-1.** The `attestation` member, when present, MUST be an object or an array of objects (multiple signatures).

**ATT-2.** Each attestation object MUST carry `algorithm` and `signature`.

**ATT-3.** `signature` MUST be base64url without padding, as defined in RFC 4648 §5.

**ATT-4.** `keyid`, when present, is a string that identifies the signing key. Its distribution and resolution are out of scope.

## 6.2 Algorithms

| Identifier | Meaning |
|---|---|
| `ed25519` | EdDSA over Ed25519 |
| `ecdsa-p256-sha256` | ECDSA P-256 with SHA-256 |
| `rsa-pss-sha256` | RSASSA-PSS with SHA-256 |

**ATT-5.** An algorithm not in this table MUST be treated as unsupported. A verifier MUST NOT silently skip an attestation it cannot verify.

## 6.3 What is signed

**ATT-6.** The signature MUST be computed over the JSON Canonicalization Scheme (JCS, RFC 8785) serialization of the record with the `attestation` member **removed**.

**ATT-7.** No other transformation is permitted: no key ordering, no whitespace normalisation, no numeric reformatting beyond what JCS specifies.

Rationale: signing the record-minus-attestation makes the signature self-contained and order-independent. Signing the artifact instead would say nothing about the claims; signing the whole record including a placeholder attestation would create a chicken-and-egg problem with no benefit.

## 6.4 Verification procedure

A verifier MUST, in order:

1. Recompute the artifact digest when the artifact is available. If it differs from `artifact.digest`, the record does not describe this artifact and verification MUST fail.
2. Check `id` equals `urn:variorum:sha256:<artifact.digest hex>`.
3. Remove `attestation` from the record.
4. Serialize with JCS.
5. Verify each signature over those bytes.

**ATT-8.** A verifier MUST fail if any declared attestation does not verify. Partial verification MUST be reported explicitly and MUST NOT be presented as a valid record.

## 6.5 Multiple signatures

**ATT-9.** When `attestation` is an array, each element MUST verify independently against the same canonical bytes.

**ATT-10.** Two signatures do not imply agreement between signers beyond the shared bytes they signed. Consumers MUST NOT infer endorsement.

## 6.6 What attestation does not establish

**ATT-11.** An attestation establishes that the holder of a key asserted the record's contents. It does not establish that the contents are true, that the artifact is lawful, or that the artifact was produced by the claimed tool.

**ATT-12.** A consumer MUST NOT describe an attested record as "verified" without stating what was verified: the signature, the digest, or both.

The distinction is not pedantry. A signed record that claims a model generated an image proves only that someone with a key made that claim.
