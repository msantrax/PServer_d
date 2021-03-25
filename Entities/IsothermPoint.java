/*
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
package isothermview;

import java.io.Serializable;
import java.util.Date;
import java.util.logging.Logger;

/**
 *
 * @author opus
 */
public class IsothermPoint implements Serializable {

    private static final Logger log = Logger.getLogger(IsothermPoint.class.getName());

    
    public IsothermPoint() {
        timestamp = System.currentTimeMillis();
    }
    
    public IsothermPoint(double ppo, double volume_g) {
        this.ppo = ppo;
        this.volume_g = volume_g;
    }

    
        private long timestamp;

    public long getTimestamp() {
        return timestamp;
    }

    public void setTimestamp(long timestamp) {
        this.timestamp = timestamp;
    }

    
    
    private double ppo;

    public double getPpo() {
        return ppo;
    }

    public void setPpo(double ppo) {
        this.ppo = ppo;
    }

        private double po;

    public double getPo() {
        return po;
    }

    public void setPo(double po) {
        this.po = po;
    }

        private double volume;

    public double getVolume() {
        return volume;
    }

    public void setVolume(double volume) {
        this.volume = volume;
    }

        private double volume_g;

    public double getVolume_g() {
        return volume_g;
    }

    public void setVolume_g(double volume_g) {
        this.volume_g = volume_g;
    }

        private boolean adsorption = true;

    public boolean isAdsorption() {
        return adsorption;
    }

    public void setAdsorption(boolean adsorption) {
        this.adsorption = adsorption;
    }

  
    
}
