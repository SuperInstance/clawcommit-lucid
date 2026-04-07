# 📓 Clawcommit Lucid

You write commits every day. Most vanish into git history. This one remembers what you actually learned.

A persistent learning journal for your development fleet, built on Cloudflare Workers. Zero dependencies, open source MIT.

**Live Demo:** [clawcommit-lucid.casey-digennaro.workers.dev](https://clawcommit-lucid.casey-digennaro.workers.dev)

## Why This Exists

You don't forget the bug you fixed at 2am, but you will forget *what you learned fixing it* in a month. Commit messages rarely capture that context. This runs alongside your work, catching insights before they slip away.

## Quick Start

This is a fork-first tool. You deploy your own instance.
1.  Fork this repository from [The Fleet](https://the-fleet.casey-digennaro.workers.dev) page.
2.  Deploy directly to Cloudflare Workers.
3.  Add a `DEEPSEEK_API_KEY` environment variable if you want AI lesson extraction.
4.  Push a commit. It appears in your journal in about 10 seconds.

## What Makes This Different

It does not scan your codebase, only what you commit. This is a memory, not a productivity dashboard. There are no streaks, scores, or notifications. You own every line. Fork it once, modify it forever.

## Features

*   **Structured Journaling:** Log commits, bugs, and insights, tagged to your projects.
*   **Skill Arc Tracking:** Group entries into progress lines like "learning KV patterns."
*   **Optional AI Distillation:** Extracts the core lesson from a commit message.
*   **Simple API:** POST JSON to add entries from any script or hook.
*   **Clean Interface:** A dark dashboard with your notes in order.
*   **Zero Dependencies:** Runs entirely on native Cloudflare APIs (Workers, KV).

## One Limitation

Your journal is stored in Cloudflare KV, which has a 10MB limit per namespace. This roughly translates to **a few thousand entries** before you need to archive or implement a rotation strategy.

## License

MIT

<div style="text-align:center;padding:16px;color:#64748b;font-size:.8rem"><a href="https://the-fleet.casey-digennaro.workers.dev" style="color:#64748b">The Fleet</a> &middot; <a href="https://cocapn.ai" style="color:#64748b">Cocapn</a></div>