# Five-minute new-user test

This is a self-serve test for someone who did not build the project. It uses fictional data, needs no Feishu account, and does not make purchases or contact venues.

1. On a machine with Git, Python 3.11+, and Codex, follow the [README installation steps](../README.en.md#start-in-30-seconds).
2. Run `python3 scripts/demo.py`. Open the printed `route-offline.html` and `day-02.svg`. Find the May 2 gallery status and the first item to cut in rain.
3. Start a fresh Codex task with this prompt (do not edit files inside the installed Skill):

   > Use `$plan-and-maintain-trips` with the fictional sample `assets/trip.example.json`. It is May 2 and I am 45 minutes late; rain has started. Keep the 10:00 gallery target on its original date and do not claim its `bookable` state means I have a ticket. Tell me what to cut first, what needs confirmation, and what changes in the day card. Work in a separate temporary trip directory.

4. Check whether the answer preserves the hard anchor, distinguishes a bookable target from a purchased ticket, and identifies the garden break as the first cut. Do not evaluate the fictional place names as real travel advice.

Feedback to send the maintainer: operating system and Python version; whether install and demo ran without help; the first unclear instruction; whether the output felt trustworthy; and one change that would make you use it for a real trip. Do not send personal itinerary files, tickets, or account details.

This exercise is not evidence that the Skill has passed human usability testing until independent users actually complete it. Track results separately from GitHub stars and clone counts.
