from math import ceil


def createsuperuser():
    from app.models import User, Role
    from app import db
    Role.insert_roles()
    user = input("please input super user:")
    result = User.query.filter_by(username=user).first()
    while result:
        user = input("please input again:")
        result = User.query.filter_by(username=user).first()
    passwd = input("please input password:")
    u = User()
    u.username = user
    u.name = user
    u.confirmed = True
    role = Role.query.filter_by(name='Administrator').first()
    u.role = role
    u.password = passwd
    db.session.add(u)
    db.session.commit()


class Pagination(object):

    def __init__(self, page, per_page, items=None):
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = len(items)
        #: the items for the current page list data
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = int(ceil(self.total / self.per_page))
        return pages

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        """
            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or (num > self.page - left_current - 1 and num < self.page + right_current) or \
                    num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    @property
    def get_items(self):
        if self.page == 1:
            data = self.items[:self.per_page]
        elif self.page == self.pages:
            data = self.items[self.per_page * (self.page - 1):]
        else:
            data = self.items[self.per_page * (self.page - 1):self.per_page * self.page]
        return data


if __name__ == "__main__":
    from app.models import User

    user = User.query.get_or_404(2)
    print(user)
    total_courses = user.courses
    print(total_courses)
    a = Pagination(page=2, per_page=8, items=total_courses)
    print(a.get_items)
