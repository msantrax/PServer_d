
package Entities;

import com.opus.syssupport.propertylink;
import com.opus.syssupport.propertyfieldmap;
import com.opus.syssupport.Config;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.logging.Logger;

import Entities.Point ;
import Entities.Isotherm_pf;


public class Isotherm {

    private static final Logger log = Logger.getLogger(Isotherm.class.getName());

    private Long _id = Long(0L);
    public Long get_Id() { return _id; }
    public void set_Id(Long _id) { this._id = _id; }

    loaded = false
    public Boolean getLoaded() { return loaded; }
    public void setLoaded(Boolean loaded) { this.loaded = loaded; }


    // Children Variables ===================================================================================================
    private ArrayList<Object> point = new ArrayList<Object>();
    private Isotherm_pf isotherm_pf;
    

    // Common / non Property / Private Variables ====================================================================
    private String owner = "instance" ;
    public String getOwner() { return owner; }
    public void setOwner(String owner) { this.owner = owner; }

    private Integer index = 0 ;
    public Integer getIndex() { return index; }
    public void setIndex(Integer index) { this.index = index; }

    private Long parent = 0 ;
    public Long getParent() { return parent; }
    public void setParent(Long parent) { this.parent = parent; }

    

    //======================================= PROPERTIES =======================================================================
    
       private Integer iso_num = 8857;

    public static final String PROP_ISO_NUM = "iso_num";

    @propertyfieldmap (propname = PROP_ISO_NUM )
    public Integer getIso_Num() {
        return iso_num;
    }

    @propertylink (propname = PROP_ISO_NUM, plink = "it_iso_num", input=false, callstate="CALLSTATE1")
    public void setIso_Num(Integer iso_num ) {
        Integer oldiso_num = this.iso_num;
        this.iso_num = iso_num;
        propertyChangeSupport.firePropertyChange(PROP_ISO_NUM, oldiso_num, iso_num);
    }


       private String iso_status = "unloaded";

    public static final String PROP_ISO_STATUS = "iso_status";

    @propertyfieldmap (propname = PROP_ISO_STATUS )
    public String getIso_Status() {
        return iso_status;
    }

    
    public void setIso_Status(String iso_status ) {
        String oldiso_status = this.iso_status;
        this.iso_status = iso_status;
        propertyChangeSupport.firePropertyChange(PROP_ISO_STATUS, oldiso_status, iso_status);
    }



    // ========================================= CONSTRUCTOR & TOOLS ===========================================================
    public Isotherm() {
        mapMethods();
    }


    private transient LinkedHashMap<String, Method> getmethods;
    public LinkedHashMap<String, Method> getMethods() { return getmethods;}

    private void mapMethods(){

        propertyfieldmap pfm;
        String fieldtag;

        getmethods = new LinkedHashMap<>();
        Class<?>c = this.getClass();

        for (Method mt : c.getDeclaredMethods() ){
            pfm = mt.getAnnotation(propertyfieldmap.class);
            if (pfm != null){
                fieldtag = pfm.propname();
                getmethods.put(fieldtag, mt);
            }
        }
    }

    public String getFieldAsString(String id){

        String out ;
        Type t;
        Method m = getmethods.get(id);
        if (m != null){
            try {
                String st = m.getReturnType().getTypeName();
                if (st.equals("java.lang.String")){
                    out = (String)m.invoke(this, null);
                    return out;
                }
                else{
                    //Class cl = Class.forName(st);
                    Object obj = m.invoke(this, null);
                    String s2 = String.valueOf(obj);
                    return s2;
                }
            } catch (IllegalAccessException | IllegalArgumentException | InvocationTargetException ex) {
                //Exceptions.printStackTrace(ex);
//            } catch (ClassNotFoundException ex) {
//                Exceptions.printStackTrace(ex);
            }
        }

        return null;
    }


    #classcode_begin

    #classcode_end


}
