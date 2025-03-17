def addConstraints(rule, conString):
    gmlstr = rule.getGMLString()
    name = rule.name
    rule = ruleGMLString(gmlstr[:-1] + conString + gmlstr[-1], name)
    return rule

def labelConstraints(rule, rpl, morph=None):
    #TODO
    return 