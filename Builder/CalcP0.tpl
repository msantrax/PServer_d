
&[PARSE]
        #parsecode_begin
        if 'Build' in self._calcp0_list[1]:
            initts = util.LocatedDate2JavaMillis(self._calcp0_list[1])
            self.init_ts = initts
            self.buildpressure.loadFromLog(self._calcp0_list[1], self._calcp0_list[2])
            if 'Amb' in self._calcp0_list[2] :
                self.initstab_ts = util.LocatedDate2JavaMillis(self._calcp0_list[2])
                mpat = re.compile(r'(\[)(.*)(\])')
                m = re.search(mpat, self._calcp0_list[2])
                if m is not None:
                    self.charge_pressure = float(m.group(2))
                    if 'mmHg' in self._calcp0_list[3]:
                        mpat = re.compile(r'(\[)(.*)\,(\d)\,(\d\d)(\])(.*)(sec )(.*)(mmHg)')
                        m = re.search(mpat, self._calcp0_list[3])
                        if m is not None:
                            self.stab_var1 = float(m.group(2))
                            self.stab_var2 = float(m.group(3))
                            self.stab_var3 = float(m.group(4))
                            self.stab_time = float(m.group(6))
                            self.amb_pressure = float(m.group(8))

                            mpat = re.compile(r'(.*)(P = )( .*)(mm Hg)')
                            m = re.search(mpat, self._calcp0_list[3])
                            if m is not None:
                                self.delta_p = float(m.group(3))
                                self.endstab_ts = util.LocatedDate2JavaMillis(self._calcp0_list[3])
                                self.end_ts = util.LocatedDate2JavaMillis(self._calcp0_list[4])

                                mpat = re.compile(r'(.*)(P0 =)( .*)(mm Hg)')
                                m = re.search(mpat, self._calcp0_list[5])
                                if m is not None:
                                    self.calc_p0 = float(m.group(3))
                                    self.populateSteps()
                                    return True

        return False
        #parsecode_end
[PARSE]&

&[DEFAULT]
        #defaultcode_begin
        self._calcp0_list = ['Calculatong P0...',
            'BuildPressure(23.802 780.000 751.697)mmHg [VOL Down] May 28 21:26:58 2013',
            '[755.9] Ambient Pressure Measurement... May 28 21:27:02 2013',
            '[0.03,3,12] 4sec 712.28mmHg P =  0.005 mm Hg   [VOL GASIN VENT Down] May 28 21:27:07 2013',
            '[VOL Down] May 28 21:27:10 2013',
            'Calculated P0 = 722.284 mm Hg'
        ]

        self.parse()
        self.loaded = True
        #defaultcode_end
[DEFAULT]&

&[LOAD]
        #loadcode_begin
        self._calcp0_list = input
        #loadcode_end
[LOAD]&

&[CLASS]
    #classcode_begin
    def populateSteps(self):
        stepnum = int((self.endstab_ts - self.initstab_ts)/1000) * 4
        steprange = (self.charge_pressure - self.amb_pressure) / stepnum

        for i in range(0, stepnum):
            self.tstamps.append(self.initstab_ts + (i * 250))
            self.values.append(self.charge_pressure - (i * steprange))
    #classcode_end
[CLASS]&
