
&[PARSE]
        #parsecode_begin
        initts = util.LocatedDate2JavaMillis(sparse)
        self.init_ts = initts
        mpat = re.compile(r'(\()(.*) (.*) (.*)(\))')
        m = re.search(mpat, sparse)
        if m is not None:
            self.param1 = float(m.group(2))
            self.param2 = float(m.group(3))
            self.param3 = float(m.group(4))

        self.end_ts = util.LocatedDate2JavaMillis(edata)
        self.populateSteps()

        loaded = True
        #parsecode_end
[PARSE]&

&[DEFAULT]
        #defaultcode_begin
        pass
        #defaultcode_end
[DEFAULT]&

&[LOAD]
        #loadcode_begin
        self.param1 =  23.800
        self.param2 = 780.000
        self.param3 = 751.601

        self.init_ts = 1369783618000
        self.end_ts = 1369783622000

        self.populateSteps()
        #loadcode_end
[LOAD]&

&[CLASS]
    #classcode_begin
    def populateSteps(self):
        stepnum = int((self.end_ts - self.init_ts)/1000) * 4
        steprange = (self.param3 - self.param1) / stepnum

        for i in range(0, stepnum):
            self.tstamps.append(self.init_ts + (i * 250))
            self.values.append(self.param1 + (i * steprange))


    #classcode_end
[CLASS]&
