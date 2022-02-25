Hi {{ preferred\_name }} -

<main>{% block main required %}{% endblock main %}</main>

--<br>
Tony Dang<br>
What I'm up to now: [{{ url\_for\('main.now', \_external=True\)[8:] }}]({{
url\_for\('main.now', \_external=True\) }})

{% if unsubscribe\_link %}
[Unsubscribe]({{ unsubscribe\_link }}) |
[Update your settings]({{ url\_for\('account.settings', \_external=True\) }})
{% endif %}
