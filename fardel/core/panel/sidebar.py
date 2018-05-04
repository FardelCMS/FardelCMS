class Section():
	def __init__(self, title):
		self.title = title
		self.links = []

	def add_link(self, link):
		self.links.append(link)

	def render_links(self):
		return "".join([link.render() for link in self.links])

	def render(self):
		return """<div class="menu_section">
<h3>{title}</h3>
<ul class="nav side-menu">
{links}
</ul>
</div>""".format(title=self.title, links=self.render_links())


class Link():
	def __init__(self, icon, title, href="#"):
		self.children = []
		self.title = title
		self.href = href
		self.icon = icon

	def add_child(self, child):
		self.children.append(child)

	def fa_chevron_down(self):
		if self.children:
			return '<span class="fa fa-chevron-down"></span>'
		return ''

	def render_children(self):
		return "".join([child.render() for child in self.children])

	def render(self):
		return """<li><a href="{href}"><i class="{icon}"></i> {title} {chevron}</a>
<ul class="nav child_menu">
{children}
</ul>
</li>""".format(icon=self.icon, title=self.title, href=self.href,
	children=self.render_children(), chevron=self.fa_chevron_down())


class ChildLink():
	def __init__(self, name, href):
		self.name = name
		self.href = href

	def render(self):
		return '<li><a href="{href}">{name}</a></li>'.format(
			href=self.href,
			name=self.name
		)


class PanelSidebar():
	def __init__(self):
		self.sections = []

	def add_section(self, section):
		self.sections.append(section)

	def render(self):
		return "".join([section.render() for section in self.sections])


panel_sidebar = PanelSidebar()