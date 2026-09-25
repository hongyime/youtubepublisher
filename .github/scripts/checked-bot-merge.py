"""Merge only reviewed bot heads with explicitly required, passing checks.

Run from the default branch; never check out a pull request with this token.
Repositories without a required Build check remain open for manual review.
Vercel projects must also make their deployment check required before enabling
this workflow. Ordinary merge rules remain authoritative at the merge request.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess

BOTS = {
    'dependabot': {'dependabot[bot]'},
    'other': {'snyk-bot', 'sourcery-ai[bot]', 'deepsource-autofix[bot]', 'copilot-swe-agent[bot]'},
}


def decision(pr, required, checks, expected_head, allowed):
    if pr.get('state') != 'open' or pr.get('draft') or pr.get('user', {}).get('login') not in allowed:
        return 'not an eligible open bot PR'
    if pr.get('head', {}).get('repo', {}).get('full_name') != pr.get('base', {}).get('repo', {}).get('full_name'):
        return 'fork PR requires manual review'
    if pr.get('base', {}).get('ref') != pr.get('base', {}).get('repo', {}).get('default_branch'):
        return 'not targeting the default branch'
    if pr.get('head', {}).get('sha') != expected_head:
        return 'PR head changed'
    if pr.get('mergeable') is not True or pr.get('mergeable_state') != 'clean':
        return 'mergeability or repository rules are not satisfied'
    if not required or not any(c.get('name') == 'Build' and c.get('workflow') == 'Build Check' for c in required):
        return 'a required Build Check / Build result is missing'
    if any(c.get('bucket') != 'pass' for c in required):
        return 'required checks have not all passed'
    if not checks or any(c.get('bucket') not in {'pass', 'skipping'} for c in checks):
        return 'other checks are unfinished or unsuccessful'
    if not any(c.get('name') == 'Build' and c.get('workflow') == 'Build Check' and c.get('state') == 'SUCCESS' for c in checks):
        return 'the current head has no successful Build Check / Build'
    return None


def gh(*args, checks=False):
    result = subprocess.run(['gh', *args], capture_output=True, text=True, timeout=45, check=False)
    # gh pr checks uses 8 for pending and 1 for failed checks. Its JSON is still
    # evaluated below. Missing/malformed output or API failures never pass.
    accepted = {0, 1, 8} if checks else {0}
    if result.returncode not in accepted:
        raise RuntimeError('GitHub request failed')
    return json.loads(result.stdout)


def inspect_and_merge(repo, number, allowed, event_head=None, dry_run=False):
    endpoint = f'repos/{repo}/pulls/{number}'
    pr = gh('api', endpoint)
    head = pr['head']['sha']
    preliminary = decision(pr, [], [], event_head or head, allowed)
    if preliminary != 'a required Build Check / Build result is missing':
        return preliminary
    fields = 'name,bucket,state,workflow'
    required = gh('pr', 'checks', str(number), '--repo', repo, '--required', '--json', fields, checks=True)
    checks = gh('pr', 'checks', str(number), '--repo', repo, '--json', fields, checks=True)
    reason = decision(pr, required, checks, head, allowed)
    if reason:
        return reason
    # Fetch metadata again after the potentially multi-request check lookup.
    latest = gh('api', endpoint)
    reason = decision(latest, required, checks, head, allowed)
    if reason:
        return reason
    if dry_run:
        return 'eligible (dry run; no merge requested)'
    # REST enforces the exact head SHA and normal branch rules. No admin bypass
    # or queued auto-merge; a refusal leaves the PR open.
    result = gh('api', '--method', 'PUT', f'{endpoint}/merge', '-f', 'merge_method=squash', '-f', f'sha={head}')
    return 'merged checked head' if result.get('merged') is True else 'merge refused; PR left open'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--group', choices=BOTS, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    repo = os.environ['GITHUB_REPOSITORY']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repo):
        raise ValueError('Invalid repository')
    event = json.loads(Path(os.environ['GITHUB_EVENT_PATH']).read_text(encoding='utf-8'))
    event_head = event.get('workflow_run', {}).get('head_sha') or event.get('sha')
    pages = gh('api', '--paginate', '--slurp', f'repos/{repo}/pulls?state=open&per_page=100')
    for pr in (pr for page in pages for pr in page):
        if pr['user']['login'] not in BOTS[args.group] or (event_head and pr['head']['sha'] != event_head):
            continue
        try:
            outcome = inspect_and_merge(repo, pr['number'], BOTS[args.group], event_head, args.dry_run)
        except (RuntimeError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired):
            outcome = 'check lookup failed or returned incomplete data; PR left open'
        print(f"PR #{pr['number']}: {outcome}")


if __name__ == '__main__':
    main()
