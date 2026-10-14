# Contributing

Thanks for helping make trip plans more reliable and easier to use. Small, focused fixes are welcome: a clearer booking-state rule, a reproducible export bug, a safer fallback, or a better example.

## Before opening an issue

- Check the README and existing issues. Say whether the problem is in the Skill's planning instructions, a script, an example, or an optional publisher.
- For changing venue hours, prices, inventory, or transit rules, include a direct official source, the date checked, and the travel date it applies to. Do not turn a past travel fact into a timeless rule.
- Remove traveler names, confirmation numbers, ticket QR codes, payment details, addresses that identify a private stay, and access tokens from logs or sample data.

## Local check

The project uses Python standard-library scripts. From the repository root:

```bash
python3 scripts/demo.py
python3 -m unittest discover -s tests -v
python3 scripts/validate_trip.py assets/trip.example.json --strict
```

The Lisbon demo is fictional and reproducible from `assets/trip.example.json`. If you change that fixture, regenerate the checked-in `examples/lisbon-coast/` outputs with the route, field-card, and field-pack scripts, then run the tests. The France guide is a redacted historical case study, not a source dataset for the generators.

## Pull requests

Explain the user-visible problem, the smallest fix, and what you verified. Keep new dependencies optional unless there is a compelling reason to add them; core planning and the local demo should still work without a Feishu account or another publishing service. If behavior changes, add a test that checks the observable outcome rather than only matching text.

This repository is published under the [MIT License](LICENSE). Contributions submitted for inclusion are expected to be compatible with it.
