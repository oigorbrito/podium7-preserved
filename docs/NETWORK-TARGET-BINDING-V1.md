# Network Target Binding V1

Status: implemented bounded hardening path.

## Problem

The original Direct HTTP V1 validates DNS resolution before handing the hostname to the standard URL opener. That blocks obviously private/non-global targets at validation time, but the opener may resolve the hostname again when it opens the socket. A hostile or compromised DNS path could therefore return a safe address during validation and a different private/internal address during connection.

## Decision

Arbitrary untrusted locators must use `acquire_bound_http`. Each request hop:

1. parses the URL and enforces the existing scheme/credential/fragment rules;
2. resolves the hostname;
3. rejects the hop if any returned address violates the network policy;
4. connects the socket to a validated IP literal from that exact resolution set;
5. preserves the original hostname for the HTTP `Host` header and, for HTTPS, TLS SNI/certificate verification;
6. repeats the entire resolution/validation/binding sequence for every redirect.

The existing `acquire_http` function remains available for controlled/trusted locators and retains its prior contract. It is not the entry point for arbitrary untrusted URLs.

## Market-first evaluation

ADR-0001 applies because network transport is infrastructure. Mature alternatives considered were the existing Python stdlib HTTP stack, Requests/urllib3, and HTTPX. Podium does not currently need a replacement general-purpose HTTP client; it needs one narrow invariant: the IP that passed policy validation must be the IP presented to the socket connection while hostname-based TLS verification remains intact.

Adding a second HTTP stack solely for that invariant would introduce dependency and integration surface and would still require a resolver/connection customization. V1 therefore `ADAPT`s mature stdlib primitives (`socket`, `ssl`, `http.client`) around the existing Direct HTTP policy/result types. This selection is an `ENGINEERING_CHOICE`, not a claim that the stdlib is universally superior.

## Fail-closed rules

- Empty or failed DNS resolution is `DNS_FAILURE`.
- Any non-global resolved address is `UNSAFE_NETWORK_TARGET` unless private-network access is explicitly enabled by policy.
- Mixed global/private DNS answers fail the whole hop rather than selecting only the global subset.
- The connector receives only validated IP literals.
- Redirect targets are not grandfathered by the original host; each hop is independently resolved and validated.
- TLS validation continues against the original hostname through SNI/default certificate verification.
- Proxy use is not introduced.

## Validation

Offline tests prove:

- loopback operation when private networking is explicitly enabled for the local test server;
- normal response and redirect behavior through the bound path;
- mixed global/private resolution rejection;
- the socket connector is called with the validated IP literal rather than the hostname;
- a second resolution that changes from global to private fails before any socket connection.

## Nonclaims

V1 is not a distributed resolver, DNSSEC implementation, proxy-safe target binder, service-mesh policy, or guarantee against compromise below the operating-system socket/TLS boundary. It does not make arbitrary URL fetching safe outside the explicit Direct HTTP policy. It closes the specific DNS validation-to-connect rebinding gap for the bound acquisition path.
