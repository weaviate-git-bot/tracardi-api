This plugin allows users to send bulk emails via the ElasticEmail API. To use this plugin, users must have an ElasticEmail account and generate an API key. Additionally, users must configure their domain in the ElasticEmail settings. Depending on the ElasticEmail plan, users may be restricted to sending emails within their own domain. 

The plugin takes any payload as input and returns a response from the ElasticEmail API. Depending on the response result, the plugin will trigger either a payload port (if the response is successful) or an error port (if the response indicates that the email was not sent). The plugin's configuration requires information about the API key, sender email, message recipient's email(s), message subject, and message content. The ElasticEmail token must be stored in Tracardis resources, and the sender's email must end with one of the domains registered in ElasticEmail. The message recipient's email can be in the form of a dot path to the email address or the address itself. The message content can be HTML or plain text, and templates can be used for both formats. 

On the ElasticEmail site, users can turn on the test mode after clicking on their username in the upper right corner. In the test mode, users can generate a test API key and use it in Tracardi for test purposes. Messages won't be sent, but ElasticEmail will act like they are, so users can test their configuration without being charged.