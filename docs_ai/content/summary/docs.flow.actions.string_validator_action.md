This plugin is designed to validate data. It requires configuration values to be specified, such as the type of validation and the string to be validated. The type of validation can be chosen from email, url, ipv4, date, time, int, float, and number_phone. The data can be a dotted notation path to a value inside profile, event, session, etc. or any string. Examples of configuration values are provided in the documentation. This node does not process input payload and will not return it on output. Output is provided through two ports, valid and invalid, depending on the validation result. The appropriate port will be launched with the payload copied as data.