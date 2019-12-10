pragma solidity ^0.4.24;
pragma experimental ABIEncoderV2;
import "./Table.sol";


contract SupplyCF {
    event CreateResult(int count);
    event InsertResult(int count);
    event UpdateResult(int count);
    event RemoveResult(int count);
    mapping(string => int) assets;
    function get_asset(string name) public returns(int){
        int asset = assets[name];
        return asset;
    }
    function set_asset(string name, int asset) public {
        assets[name] = asset;
    }
    function create_company_table() public returns(int){
        TableFactory tf = TableFactory(0x1001); //The fixed address is 0x1001 for TableFactory
        int count = tf.createTable("company_t", "dummy", "name, address, type");
        emit CreateResult(count);

        return count;
    }
    // register for companies
    function register(string _name, string _address, string _type) public returns (int count){
        TableFactory tf = TableFactory(0x1001);
        Table table = tf.openTable("company_t");
        Entry entry_to_insert = table.newEntry();
        entry_to_insert.set("dummy", "active");
        entry_to_insert.set("name", _name);
        entry_to_insert.set("address", _address);
        entry_to_insert.set("type", _type);
        emit InsertResult(count);
        count = table.insert("active", entry_to_insert);
        assets[_name] = 1000;
        if(keccak256(_name) == keccak256("bank")){
            assets[_name] = 1000000;
        }
        return count;
    }
    function select_registered() public returns (string[], string[], string[]){
        TableFactory tf = TableFactory(0x1001);
        Table table = tf.openTable("company_t");
        Entries entries = table.select("active", table.newCondition());
        string[] memory name_list = new string[](uint256(entries.size()));
        string[] memory type_list = new string[](uint256(entries.size()));
        string[] memory addr_list = new string[](uint256(entries.size()));
        for(int i=0; i<entries.size(); ++i) {
            Entry entry = entries.get(i);
            name_list[uint256(i)] = entry.getString("name");
            type_list[uint256(i)] = entry.getString("type");
            addr_list[uint256(i)] = entry.getString("address");
        }
        return (name_list, type_list, addr_list);

    }
    // whether a company given name is registered or not.
    function is_registered(string name) public returns (int count){
        TableFactory tf = TableFactory(0x1001);
        Table table = tf.openTable("company_t");
        Condition condition = table.newCondition();
        condition.EQ("name", name);
        Entries entries = table.select("active", condition);
        if (0 == uint256(entries.size())) {
            return -1;
        } else {
            return 1;
        }
    }
    //create table
    function create_receipt_table() public returns(int){
        TableFactory tf = TableFactory(0x1001); //The fixed address is 0x1001 for TableFactory
        int count = tf.createTable("receipt_t", "dummy", "from, to, amount,status, due_date");
	      emit CreateResult(count);

	      return count;
    }
    function extract_info(Entries entries) public returns(string[], string[], int[], string[], string[]){
        string[] memory from_list = new string[](uint256(entries.size()));
        string[] memory to_list = new string[](uint256(entries.size()));
        int[] memory amt_list = new int[](uint256(entries.size()));
        string[] memory status_list = new string[](uint256(entries.size()));
        string[] memory due_date_list = new string[](uint256(entries.size()));
        for(int i = 0; i < entries.size(); ++i) {
            Entry entry = entries.get(i);
            from_list[uint256(i)] = entry.getString("from");
            to_list[uint256(i)] = entry.getString("to");
            amt_list[uint256(i)] = entry.getInt("amount");
            status_list[uint256(i)] = entry.getString("status");
            due_date_list[uint256(i)] = entry.getString("due_date");
        }
        return (from_list, to_list, amt_list,status_list, due_date_list);

    }
    //select records
    function select(string company, int mode) public constant returns(string[], string[], int[], string[], string[]){
        TableFactory tf = TableFactory(0x1001);
        Table table = tf.openTable("receipt_t");
        Condition condition = table.newCondition();
        if(mode == 1){
            condition.EQ("from", company);
        }
        else if(mode == 0){
            condition.EQ("to", company);
        }
        else if(mode == 2){
            condition.EQ("status", "submitted");
        }
        Entries entries = table.select("active", condition);
        return extract_info(entries);
    }
    //insert records
    function insert(string _from, string _to, int amt, string sta, string dd) public returns(int) {
        TableFactory tf = TableFactory(0x1001);
        Table table = tf.openTable("receipt_t");
        Entry entry_to_insert = table.newEntry();
        entry_to_insert.set("dummy", "active");
        entry_to_insert.set("from", _from);
        entry_to_insert.set("to", _to);
        entry_to_insert.set("amount", amt);
        entry_to_insert.set("status", sta);
        entry_to_insert.set("due_date", dd);
        int count = table.insert("active", entry_to_insert);
        emit InsertResult(count);
        return count;
    }
    function purchasing(string _from, string _to, int amt, string dd) public returns(int){
        if(is_registered(_from) == -1 || is_registered(_to) == -1){
            return -3;
        }
        int count = insert(_from, _to, amt, "submitted", dd);
        if(count == 1){
            return 1;
        }
        else{
            return -1;
        }
    }
    //the receipt on due day
    function due_day(string _from, string _to, int _amount, string _expiration) public returns(int){
        remove(_from, _to, _amount, _expiration);
        if(keccak256(_to) == keccak256("bank")){
            assets[_from] -= _amount;
        }
    }
    function transfer (string _from, string _to,string _to_to, int prev_amt,int _amount, string dd) public returns(int) {
        if(is_registered(_from) == -1 || is_registered(_to) == -1){
            return -3;
        }
        update(_from, _to, prev_amt - _amount,"submitted", dd);
        insert(_from, _to_to, _amount,"submitted", dd);
        return 1;
    }
    //borrow money from bank
    function borrow_money(string _from, string _to, int _amount, string dd) public {
        insert(_from, _to, _amount,  "submitted", dd);
    }
    //update records
    function update(string _from, string _to, int amt, string sta, string dd) public returns(int) {
        TableFactory tf = TableFactory(0x1001);
        Table table = tf.openTable("receipt_t");
        Entry entry = table.newEntry();
        entry.set("dummy", "active");
        entry.set("from", _from);
        entry.set("to", _to);
        entry.set("amount", amt);
        entry.set("status", sta);
        entry.set("due_date", dd);
        Condition condition = table.newCondition();
        condition.EQ("from", _from);
        condition.EQ("to", _to);
        if(keccak256(sta) == keccak256("authorized") && keccak256(_to) == keccak256("bank")){
            assets[_from] += amt;
        }
        int count = table.update("active", entry, condition);
        emit UpdateResult(count);
        return count;
    }
    //remove records
    function remove(string _from, string _to, int amt, string dd) public returns(int){
        TableFactory tf = TableFactory(0x1001);
        Table table = tf.openTable("receipt_t");
        Condition condition = table.newCondition();
        condition.EQ("from", _from);
        condition.EQ("to", _to);
        condition.EQ("amount", amt);
        condition.EQ("due_date", dd);

        int count = table.remove("active", condition);
        emit RemoveResult(count);


        //update the total money borrowed from others and money lent to others.
        return count;
    }
}
