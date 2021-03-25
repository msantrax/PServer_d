
&[PACKAGE]
package $PACKAGE;
[PACKAGE]&

&[IMPORTS]
import com.opus.syssupport.SMTraffic;
import com.opus.syssupport.VirnaPayload;
import com.opus.syssupport.propertylink;
import com.opus.syssupport.propertyfieldmap;
import java.util.ArrayList;
import java.util.logging.Logger;

import middlestripb.MongoLink ;
import middlestripb.EntityDescriptor ;
import middlestripb.EntityDescriptors ;
import middlestripb.QueuedDescriptors ;

import org.bson.Document;
import org.bson.types.ObjectId ;
import com.mongodb.client.model.Filters ;

$IMPORTS
[IMPORTS]&

&[CLASSDEF]
public class $CLASSNAME extends Entity {

    private static final Logger log = Logger.getLogger($CLASSNAME.class.getName());

    private transient MongoLink mongolink;

    private Long suid = 0L ;
    public Long getSuid() { return suid; }
    public void setSuid(Long suid) { this.suid = suid; }

    private ObjectId _id ;
    public ObjectId get_Id() { return _id; }
    public void set_Id(ObjectId _id) { this._id = _id; }

    Boolean cascade = false ;
    public Boolean getCascade() { return cascade; }
    public void setCascade(Boolean cascade) { this.cascade = cascade; }

[CLASSDEF]&



&[INITCHILDRENS]
    // Children Variables ==========================================================================================
$CHILDINITS
[INITCHILDRENS]&



&[INITVARS]
    // Common / non Property / Private Variables ====================================================================
$INITVARS
[INITVARS]&


&[PROPERTIES]
    //======================================= PROPERTIES ============================================================
    $PROPERTIES



[PROPERTIES]&


&[CONSTRUCTOR]
    // ========================================= CONSTRUCTOR & TOOLS =================================================
    public $CLASSNAME() {

    }


    private static $CLASSNAME instance;
    public static $CLASSNAME getInstance(Long parent){

        Object temp;
        instance = new $CLASSNAME();
        instance.mongolink = MongoLink.getInstance();
        instance.suid = instance.mongolink.getSuid();
        instance.setParent(parent);

        EntityDescriptor ed = new EntityDescriptor()
                .setSuid(instance.suid)
                .setInstance(instance);

        instance._descriptor = ed;

        $REGISTRIES

        EntityDescriptor ed1 = instance.mongolink.registerEntity(ed);
        if (ed1 != null){
            instance = ($CLASSNAME)ed1.getInstance();
            ed1.setStatus(EntityDescriptor.Status.UPDATE);
        }
        return instance;
    }

    @Override
    public String toString(){
        return String.valueOf(suid);
    }


[CONSTRUCTOR]&

&[REGISTRY]
        temp = $RCHILDCLASS.getInstance(parent).getSuid();
        instance$RCHILDVAR = temp ;
[REGISTRY]&

&[REGISTRYLIST]
        instance$RCHILDVAR = new $RCHILDINIT() ;
        temp = $RCHILDCLASS.getInstance(parent).getSuid() ;
        instance$RCHILDVAR.add(temp) ;
[REGISTRYLIST]&


}

&[PROPERTY]
       private $TYPE $NAME = $VALUE;

    public static final String PROP_$UPNAME = "$NAME";

    @propertyfieldmap (propname = PROP_$UPNAME )
    public $TYPE get$CAPNAME() {
        return $NAME;
    }

    $PROPERTYLINK
    public void set$CAPNAME($TYPE $NAME ) {
        $TYPE old$NAME = this.$NAME;
        this.$NAME = $NAME;
        propertyChangeSupport.firePropertyChange(PROP_$UPNAME, old$NAME, $NAME);
    }

[PROPERTY]&

&[LOADCHILDREN]

    @Override
    public boolean loadChildren(boolean cascade, SMTraffic smm){

        EntityDescriptors ed = mongolink.getLoaded_descriptors();
        QueuedDescriptors tsk = mongolink.getTask_descriptors();
        boolean loadrequest = false;

        if (smm != null){
            EntityDescriptor rooted = new EntityDescriptor()
                    .setClazz($CHILDRENCLASS.class)
                    .setBson(Filters.eq("suid", suid))
                    .setCascade(Boolean.FALSE)
                    .setAction(smm)
                    .setLoaded(true)
                    .setSuid(suid);
            tsk.offer(rooted);
        }

        $LOADCHILDREN

        return loadrequest;
    }
[LOADCHILDREN]&

&[LOADCHILD]
        if ($CHILDVAR instanceof Long){
                $CHILDCLASS t_$CHILDVAR = ($CHILDCLASS)ed.findById((Long)$CHILDVAR, true);
                if (t_$CHILDVAR != null) {
                    $CHILDVAR = t_$CHILDVAR;
                    if (cascade) t_$CHILDVAR.loadChildren(cascade, null);
                }
                else{
                    tsk.offer(new EntityDescriptor()
                            .setClazz($CHILDCLASS.class)
                            .setBson(Filters.eq("suid", (Long)$CHILDVAR))
                            .setCascade(cascade));
                }
            }
[LOADCHILD]&

&[LOADLISTCHILD]
        if ($CHILDVAR.get(0) instanceof Long){
            for (int i = 0; i < $CHILDVAR.size(); i++) {
                Long $CHILDVAR_suid = (Long)$CHILDVAR.get(i);
                $CHILDCLASS t_$CHILDVAR = ($CHILDCLASS)ed.findById((Long)$CHILDVAR_suid, true);
                if (t_$CHILDVAR != null) {
                    $CHILDVAR.set(i, t_$CHILDVAR);
                    if (cascade) t_$CHILDVAR.loadChildren(cascade, null);
                }
                else{
                    tsk.offer(new EntityDescriptor()
                            .setClazz($CHILDCLASS.class)
                            .setBson(Filters.eq("suid", $CHILDVAR_suid))
                            .setCascade(cascade));
                }
            }
        }
[LOADLISTCHILD]&

&[SERVICECHILDREN]
    $SERVICECHILDREN
[SERVICECHILDREN]&

&[SERVICECHILD]

    public ArrayList<$CHILDCLASS> getObj$CAPCHILDVAR(){

        ArrayList<$CHILDCLASS> lpts = new ArrayList<>();

        for (int i = 0; i < $CHILDVAR.size(); i++) {
            if ($CHILDVAR.get(i) instanceof Long){
                break;
            }
            else if ($CHILDVAR.get(i) instanceof $CHILDCLASS){
                $CHILDCLASS pt = ($CHILDCLASS)$CHILDVAR.get(i);
                lpts.add(pt);
            }
        }
        return lpts;
    }

    public ArrayList<Long> get$CAPCHILDVAR(){

        ArrayList<Long> lpts = new ArrayList<>();

        for (int i = 0; i < $CHILDVAR.size(); i++) {
            if ($CHILDVAR.get(i) instanceof Long){
                lpts.add((Long)$CHILDVAR.get(i));
            }
            else if ($CHILDVAR.get(i) instanceof $CHILDCLASS){
                $CHILDCLASS pt = ($CHILDCLASS)$CHILDVAR.get(i);
                lpts.add(pt.getSuid());
            }
        }
        return lpts;
    }

    public $CHILDCLASS add$CHILDCLASS(){

        $CHILDCLASS pt;

        if ($CHILDVAR.get(0) instanceof Long){
            loadChildren(true, null);
        }

        pt = ($CHILDCLASS)$CHILDVAR.get(0);
        if (pt.getOwner().equals("instance")){
            pt.setOwner("activated");
        }
        else{
            pt = $CHILDCLASS.getInstance(parent);
            pt.setOwner("added");
            $CHILDVAR.add(pt);
            pt.loadChildren(true, null);
        }
        return pt;
    }

[SERVICECHILD]&

&[DBLINK]
    @Override
    public Document getDocument(){

        Document doc = new Document()
                $DBUPLINKS
                ;
        return doc;
    }

    @Override
    public Entity loadEntity(Document document, EntityDescriptor ed){

        $DBDOWNLINKS

        this.mongolink = MongoLink.getInstance();
        ed.setSuid(suid);

        EntityDescriptor ned = new EntityDescriptor()
                .setSuid(this.suid)
                .setInstance(this);

        this._descriptor = ned;
        mongolink.getLoaded_descriptors().add(ned);
        ed.setLoaded(true);
        
        return this;

    }


[DBLINK]&


#====================================================================================================================
&[CLASSMETHODS]
$CMETHODS

}
[CLASSMETHODS]&
