This documentation text provides information about the core definitions of an action in the Tracardi workflow system. It explains that an action is a single task in the workflow, consisting of input and output ports. It also explains that the action is a code in the system, and the input and output ports are mapped to the input parameters and return values of a function in the code. The text also explains that the action node can have only one input port and many output ports, and that each action node has a reference to certain data, such as the node id, debug flag, event, profile, session, flow diagram, execution graph, node information, console, and metrics object. Additionally, the text explains that the action has three core methods: build, __init__, and run, as well as auxiliary functions such as register and validate. Finally, the text provides a list of available actions in Tracardi and how to configure them using a JSON file or a GUI form.