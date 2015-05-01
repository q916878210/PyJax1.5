__author__ = 'Sean Mead'


class Var(type):
    name = '<span class="blue-text">%s</span>'
    value = '<span class="green-text">="%s"</span>'
    tag_out = '<span>&lt;%s&nbsp;</span>%s&gt;<span>%s</span>&lt;/%s&gt;'


def write(node):
    html = '<br>'
    child = node.parent().children()[0]
    c_i = ' '.join([(Var.name % key) + ((Var.value % value) if value is not True else '') for key, value in child.attr.iteritems()])
    html += Var.tag_out % (child.tag, c_i.strip(), child.inner(), child.tag)
    return html