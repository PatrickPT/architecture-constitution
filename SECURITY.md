# Security policy

## Supported version

The latest commit on `main`. There are no releases yet.

## Report a vulnerability

Use GitHub's private vulnerability reporting: open the repository's Security tab and choose "Report a
vulnerability". Please do not open a public issue for a vulnerability, and do not attach real code, private paths
or credentials to a report. An invented example is enough.

## What counts in particular

The skill is text that agents follow with the permissions of the session they run in. So these count:

- Wording that makes an agent run, install or fetch something the task doesn't need, or act outside the
  repository it works on.
- Wording that makes an agent weaken a check, skip a test or approve a change it should block.
- A principle or article that advises an insecure practice.
- Anything in the consistency check or CI that runs untrusted input or exposes a secret.

## What the skill does

It reads the repository it is asked to work on and the two files in its `references/` folder. `write` changes
that repository through one pull request; `review` changes nothing. It holds no credentials and asks for none.

There is no bug bounty.
