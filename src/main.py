import time
import requests
import os.path

# Prepare functions

lines = []

def add_line(x): 
	lines.append(x)

def flush_lines():
	lines.clear()

def print_lines():
	temp_lines = lines.copy()
	flush_lines()
	return "\n".join(temp_lines)

# Time

gmt_00 = time.gmtime().tm_hour
gmt_07 = gmt_00 + 7

if gmt_07 > 23: gmt_07 -= 24

if gmt_07 == 0: h12 = "12am"
elif gmt_07 < 12: h12 = f"{gmt_07}am"
elif gmt_07 == 12: h12 = "12pm"
else: h12 = f"{gmt_07-12}pm"

if len(str(gmt_07)) == 1: h24 = f"0{gmt_07}"
else: h24 = gmt_07

if gmt_07 > 6 and gmt_07 < 19: emoji = ":sunny:"
else: emoji = ":crescent_moon:"

# Commits and events

commits = []
events = []

responseReq = requests.get('https://api.github.com/users/Hans5958/events/public')
response = responseReq.json()

for event in response:
	repo_link = f'https://github.com/{event["repo"]["name"]}'
	repo_link_md = f'[{event["repo"]["name"]}]({repo_link})'
	payload = event["payload"]
	type = event["type"]
	
	timestamp = event["created_at"]
	
	if type == "CreateEvent":
		events.append(f'Created {payload["ref_type"]} `{payload["ref"]}` on {repo_link_md} ({timestamp})')
	
	elif type == "DeleteEvent":
		events.append(f'Deleted {payload["ref_type"]} `{payload["ref"]}` on {repo_link_md} ({timestamp})')
		
	elif type == "ForkEvent":
		events.append(f'Made fork of {repo_link_md} on [{payload["forkee"]["full_name"]}](https://github.com/{payload["forkee"]["full_name"]}) ({timestamp})')
	
	elif type == "GollumEvent":
		events.append(f'Updated wiki on {repo_link_md} ({timestamp})')
	
	elif type == "IssueCommentEvent":
		issue_number = payload["issue"]["number"]
		events.append(f'{payload["action"].capitalize()} comment on issue/PR [#{issue_number}]({repo_link}/issues/{issue_number}) on {repo_link_md} ({timestamp})')
	
	elif type == "IssuesEvent":
		issue_number = payload["issue"]["number"]
		events.append(f'{payload["action"].capitalize()} issue [#{issue_number}]({repo_link}/issues/{issue_number}) on {repo_link_md} ({timestamp})')

	elif type == "PullRequestEvent":
		pr_number = payload["pull_request"]["number"]
		events.append(f'{payload["action"].capitalize()} pull request [#{pr_number}]({repo_link}/issues/{pr_number}) on {repo_link_md} ({timestamp})')
	
	elif type == "PullRequestReviewCommentEvent":
		pr_number = payload["pull_request"]["number"]
		events.append(f'{payload["action"].capitalize()} comment on a review on PR [#{pr_number}]({repo_link}/issues/{pr_number}) on {repo_link_md} ({timestamp})')
	
	elif type == "PublicEvent":
		events.append(f'Made repo {repo_link_md} public ({timestamp})')
	
	elif type == "PushEvent":
		# events.append(f'Pushed commits on {repo_link_md} ({timestamp})')
		branch = payload["ref"][11:]
		for commit in payload["commits"]:
			if commit["author"]["name"] == "Hans5958":
				hash = commit['sha']
				commits.append(f"[`{hash[:7]}`]({repo_link}/commit/{hash}) {commit['message'].splitlines()[0]} ({repo_link_md}, [{branch}]({repo_link}/tree/{branch}))")
	
	elif type == "ReleaseEvent":
		events.append(f'{payload["action"].capitalize()} version ({payload["release"]["tag_name"]}) on {repo_link_md} ({timestamp})')
	
	elif type == "WatchEvent":
		events.append(f'{payload["action"].capitalize()} {repo_link_md} ({timestamp})')
	
	else: # MemberEvent and SponsorEvent not supported
		events.append(f'{type} on {repo_link_md} ({timestamp})')

# Get last dev commit

if os.path.isfile("../last-dev-commit.txt"):
	last_dev_commit = open("../last-dev-commit.txt", "r").read().rstrip()
else: 
	responseReq = requests.get('https://api.github.com/repos/Hans5958/Hans5958/branches/dev')
	response = responseReq.json()
	last_dev_commit = response["commit"]["sha"]
	with open("../last-dev-commit.txt", "w") as f:
		f.write(last_dev_commit)

# Replacing

with open('src/base.md', 'r') as f:
	file = f.read()
	def replace(replace_string, to_string): 
		global file	
		file = file.replace(replace_string, to_string)
	
	replace("{{hour-24}}", str(h24))
	replace("{{hour-12}}", str(h12))
	replace("{{time-emoji}}", emoji)

	if gmt_07 < 7:
		replace("{{status-from-time}}", "*There is a great chance that I'm offline, so I'm sorry that I can't respond to you currently.*")
	elif gmt_07 < 9:
		replace("{{status-from-time}}", "*I will will be online in a few hours or so.*") 
	elif gmt_07 < 22:
		replace("{{status-from-time}}", "*I'm online, doing stuff, and is able to respond to inquiries.*")
	else:
		replace("{{status-from-time}}", "*I'm online, but only if I'm on a weekend, or there's nothing to do tommorow morning.*")

	for line in commits[:10]:
		add_line(f"- {line}")
	replace("{{last-commits}}", print_lines())

	for line in events[:10]:
		add_line(f"- {line}")
	replace("{{last-events}}", print_lines())

	replace("{{last-updated}}", time.strftime('%d/%m/%Y, %H:%M:%S UTC', time.localtime()))
	replace("{{commit-hash}}", f"[`{last_dev_commit[:7]}`](https://github.com/Hans5958/Hans5958/commit/{last_dev_commit})")

with open("README.md", "w", encoding="utf-8") as f:

	f.write(file)

print(f'::set-output name=TIMESTAMP::{time.strftime("%Y-%m-%dT%H:%M:%S%z", time.localtime())}')

# add_line("### Last five commits")
# add_line("")

# for line in commits[:5]:
#	add_line(f"- {line}")
	
# add_line("")
# add_line("### Last five events")
# add_line("")

# for line in events[:5]:
# 	add_line(f"- {line}")
	
# add_line("")
# add_line("</details>")
# add_line("")
# add_line(f"*Last updated: {}*")


# print("\n".join(lines))