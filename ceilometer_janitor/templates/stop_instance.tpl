From: STS Stack <sts-stack-noreply@canonical.com>
To: STS User <{{ email }}>
Subject: STS Stack - Idle instances.

Dear User.

The following list of instances were identified as idle:  

{% for instance in instances %}
- Name: {{instance.name}} , Id: {{ instance.id }}
{% endfor %}

Those instances will be stopped effectively now. If you are still using
them please re-start them using nova client, if not please 
destroy them to free resources.

Thanks.

STS Stack admin.
