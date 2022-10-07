#  ██████╗ ██╗████████╗██╗      █████╗ ██████╗     ██████╗  █████╗ ███████╗██╗  ██╗██████╗  ██████╗  █████╗ ██████╗ ██████╗ 
# ██╔════╝ ██║╚══██╔══╝██║     ██╔══██╗██╔══██╗    ██╔══██╗██╔══██╗██╔════╝██║  ██║██╔══██╗██╔═══██╗██╔══██╗██╔══██╗██╔══██╗
# ██║  ███╗██║   ██║   ██║     ███████║██████╔╝    ██║  ██║███████║███████╗███████║██████╔╝██║   ██║███████║██████╔╝██║  ██║
# ██║   ██║██║   ██║   ██║     ██╔══██║██╔══██╗    ██║  ██║██╔══██║╚════██║██╔══██║██╔══██╗██║   ██║██╔══██║██╔══██╗██║  ██║
# ╚██████╔╝██║   ██║   ███████╗██║  ██║██████╔╝    ██████╔╝██║  ██║███████║██║  ██║██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
#  ╚═════╝ ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═════╝     ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ 
#                                                                                                          by m.maragkoudakis
import gitlab
import datetime
from jinja2 import Template


def human_readable_time(time_in_sec, rounded=True):
    if time_in_sec == 0:
        return '0h'
    hours = time_in_sec // (60 * 60)
    seconds = time_in_sec % (60 * 60)
    minutes = seconds // 60
    seconds %= 60
    time_str = ''
    if not rounded:
        if hours != 0:
            time_str += str(hours) + 'h'
        if not minutes == 0:
            if time_str != '':
                time_str += ' '
            time_str += str(minutes) + 'm'
        if seconds != 0:
            if time_str != '':
                time_str += ' '
            time_str += str(seconds) + 's'
    else:
        if minutes > 30:
            hours += 1
        time_str += str(hours) + 'h'
    return time_str


def date_formatter(date_str):
    if date_str == None:
        return 'No due date'
    due_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    due_date_str = due_date.strftime("%b %d, %Y")
    current_date = datetime.datetime.now()
    difference = due_date - current_date
    if difference.total_seconds() < 0:
        return due_date_str + " (expired)"
    days = difference.days
    # years = days // 365
    # days %= 365
    months = days // 30
    days %= 30
    remaining_time = ''
    # if years != 0:
    #   if years > 1:
    #     remaining_time += str(years)+' years'
    #   else:
    #     remaining_time += '1 year'
    # elif months != 0:
    if months != 0:
        if remaining_time != '':
            remaining_time += ' '
        if months > 1:
            remaining_time += str(months) + ' months'
        else:
            remaining_time += '1 month'
    elif days != 0:
        if remaining_time != '':
            remaining_time += ' '
        if days > 1:
            remaining_time += str(days) + ' days'
        else:
            remaining_time += '1 day'

    if remaining_time == '':
        remaining_time = '0 days'
    return due_date_str + ' (remaining: ' + remaining_time + ')'


def template_filters(pxm_list):
    buttons = ""
    for pxm in pxm_list:
        buttons += """<button type="button" data-filter=".""" + pxm.lower().replace('::', '-') + """ " class="mb-1">""" + pxm.split("::")[1] + """</button>"""
        buttons += '\n          '

    return buttons


def human_readable_remaining(hours_spent, hours_total):
    if hours_spent < hours_total:
        return human_readable_time(hours_total - hours_spent).split()[0] + ' remaining'
    elif hours_spent == hours_total:
        return '0h remaining'
    else:
        return '+' + human_readable_time(hours_spent - hours_total).split()[0]


def generate_milestone_div(project_path, project_name, milestone_name, hours_spent, hours_total, due_date, pxm=None):
    due_color = "blue"
    pxm_class = 'pxm-pill-blue'
    if pxm is None or pxm == "PXM:Unassigned":
        pxm = 'PXM:Unassigned'
        pxm_class = 'pxm-pill-orange'
    due_date_formatted = date_formatter(due_date)
    pxm_data = pxm.lower().split('::')

    pxm_data = pxm_data[0] + '-' + pxm_data[1]
    if due_date_formatted == 'No due date':
        due_color = 'red'
    elif "(expired)" in due_date_formatted:
        due_color = 'purple'
    elif "remaining: 1 month" in due_date_formatted:
        due_color = 'orange'
    pill_style = 'pill pill-green'
    percentage = hours_spent / hours_total * 100
    bar_color = "percentage-bar"
    if percentage > 80:
        pill_style = 'pill pill-orange'
    if percentage > 100:
        percentage = hours_total / hours_spent * 100
        bar_color = "percentage-bar red-bar"
        pill_style = 'pill pill-red'
    if hours_total == 1:
        hours_total = 0

    if due_date is None:
        due_date = 'notset'

    with open('milestone_template.html') as file_:
        template = Template(file_.read())
    milestone = template.render(pxm_data=pxm_data,
        project_name=project_name,
        due_date=due_date,
        milestone_href="https://agile.eummena.org/desk/" + project_path + "/-/issues/?milestone_title=" + milestone_name.replace(
            ' ', '%20') + "&first_page_size=20",
        milestone_name=milestone_name,
        pxm_class=pxm_class,
        pxm=pxm,
        bar_color=bar_color,
        bar_width='style="  width:' + str(percentage) + '% "',
        hours_spent=human_readable_time(hours_spent),
        hours_estimated=human_readable_time(hours_total),
        pill_style='class="' + pill_style + '"',
        remaining=human_readable_remaining(hours_spent, hours_total),
        due_color='class="' + due_color + '"',
        due_date_formatted=due_date_formatted
    )
    return milestone


class Milestone:
    def __init__(self, project_id, project_name, milestone_id, title, due_date, start_date, pxm=None):
        self.project_id = project_id
        self.project_name = project_name
        self.milestone_id = milestone_id
        self.title = title
        self.due_date = due_date
        self.start_date = start_date
        if pxm:
            self.pxm = pxm
        else:
            self.pxm = ''

    def __str__(self):
        return str((self.project_id, self.milestone_id, self.title, self.due_date, self.start_date, self.pxm))


def get_group_milestones(gitlab_connection, group_id, output=False):
    max_count = 100
    count = 0
    group_milestones = set()
    slaGroup = gitlab_connection.groups.get(group_id)
    projects = slaGroup.projects.list(per_page=100)
    if output:
        print(len(projects))
    for p in projects:
        project = gitlab_connection.projects.get(p.id)
        pxm_tag = 'PXM:Unassigned'
        for tag in project.tag_list:
            if 'PXM' in tag:
                pxm_tag = tag
        if output:
            print(p.id)
        milestones = project.milestones.list(state='active')
        if output:
            print('--', len(milestones))
        for m in milestones:
            group_milestones.add((p.id, p.name, m.id, m.title, m.due_date, m.start_date, pxm_tag))
            if output:
                print('---', m.id, m.title, m.due_date, m.start_date)
    return [Milestone(*m) for m in group_milestones]


def generate_dashboard_html(gitlab_connection, milestones_list, note_href=None):
    milestones = ""
    pxms = []
    for milestone in milestones_list:
        pxm = milestone.pxm
        if pxm not in pxms and pxm != 'PXM::Unassigned':
            pxms.append(pxm)
        total_time_spent = 0
        total_time_estimate = 0
        project = gitlab_connection.projects.get(milestone.project_id)
        milestone_issues = project.issues.list(all=True, milestone=milestone.title)
        for issue in milestone_issues:
            if 'uncosted' in issue.labels or 'untime' in issue.labels:
                continue
            time_stats = issue.time_stats()
            total_time_spent += time_stats["total_time_spent"]
            total_time_estimate += time_stats["time_estimate"]
        if total_time_estimate == 0:
            if total_time_spent == 0:
                total_time_estimate = 1
            else:
                total_time_estimate = total_time_spent
        milestones += generate_milestone_div(project.path, milestone.project_name, milestone.title, total_time_spent,
                                             total_time_estimate,
                                             milestone.due_date, milestone.pxm)
    pxms.sort()
    # We want to add 'PXM::Unassigned' as the last option on the filter buttons
    pxms.append('PXM::Unassigned')
    filters = template_filters(pxms)
    if note_href is not None:
        milestones += "\n" +""""
        <div style="width: 100vw; padding: 5vw;">
			<h2 name="project">Shared Notes</h2>
			<p>A page for keeping notes:</p>
			<iframe src=" """ + note_href + """ " height="500" width="100%" title="Dashboard Notes"></iframe>	
		</div>"""
    with open('dash_template.html') as file_:
        dash_template = Template(file_.read())

    with open('style.css') as style_file:
        styles = '<style>\n' + style_file.read() + '\n  </style>'

    dashboard = dash_template.render(
        styles=styles,
        filters=filters,
        milestones=milestones
    )

    return dashboard


def main():
    authToken = "[YOUR_GITLAB_AUTH_TOKEN]"
    url = "[SELFHOSTED_GITLAB_URL]"
    gl = gitlab.Gitlab(URL, oauth_token=authToken)
    group_id = 3 #ENTER THE ID NUMBER OF THE WANTED GITLAB GROUP
    milestones = get_group_milestones(gl, group_id)
    print("Group Milestones:", len(milestones))

    dashboard = generate_dashboard_html(gl, milestones)
    with open('gitlab_dashboard.html', 'w+') as output:
        output.write(dashboard)

if __name__ == '__main__':
    main()