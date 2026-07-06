from . import _get_conn

STATE_DISTRICTS = {
    "Andaman and Nicobar Islands": ["Nicobars", "North And Middle Andaman", "South Andamans"],
    "Andhra Pradesh": [
        "Alluri Sitharama Raju", "Anakapalli", "Ananthapuramu", "Annamayya",
        "Bapatla", "Chittoor", "Dr. B.R. Ambedkar Konaseema", "East Godavari",
        "Eluru", "Guntur", "Kakinada", "Krishna", "Kurnool", "Markapuram",
        "Nandyal", "Ntr", "Palnadu", "Parvathipuram Manyam", "Polavaram",
        "Prakasam", "Sri Potti Sriramulu Nellore", "Sri Sathya Sai",
        "Srikakulam", "Tirupati", "Visakhapatnam",
    ],
    "Arunachal Pradesh": [
        "Anjaw", "Bichom", "Changlang", "Dibang Valley", "East Kameng",
        "East Siang", "Kamle", "Keyi Panyor", "Kra Daadi", "Kurung Kumey",
        "Leparada", "Lohit", "Longding", "Lower Dibang Valley", "Lower Siang",
        "Lower Subansiri", "Namsai", "Pakke Kessang", "Papum Pare",
        "Shi Yomi", "Siang", "Tawang", "Tirap", "Upper Siang", "Upper Subansiri",
    ],
    "Assam": [
        "Bajali", "Baksa", "Barpeta", "Biswanath", "Bongaigaon", "Cachar",
        "Charaideo", "Chirang", "Darrang", "Dhemaji", "Dhubri", "Dibrugarh",
        "Dima Hasao", "Goalpara", "Golaghat", "Hailakandi", "Hojai", "Jorhat",
        "Kamrup", "Kamrup Metro", "Karbi Anglong", "Kokrajhar", "Lakhimpur",
        "Majuli", "Marigaon",
    ],
    "Bihar": [
        "Araria", "Arwal", "Aurangabad", "Banka", "Begusarai", "Bhagalpur",
        "Bhojpur", "Buxar", "Darbhanga", "Gaya", "Gopalganj", "Jamui",
        "Jehanabad", "Kaimur (Bhabua)", "Katihar", "Khagaria", "Kishanganj",
        "Lakhisarai", "Madhepura", "Madhubani", "Munger", "Muzaffarpur",
        "Nalanda", "Nawada", "Pashchim Champaran",
    ],
    "Chandigarh": ["Chandigarh"],
    "Chhattisgarh": [
        "Balod", "Balodabazar-Bhatapara", "Balrampur-Ramanujganj", "Bastar",
        "Bemetara", "Bijapur", "Bilaspur", "Dakshin Bastar Dantewada",
        "Dhamtari", "Durg", "Gariyaband", "Gaurela-Pendra-Marwahi",
        "Janjgir-Champa", "Jashpur", "Kabeerdham",
        "Khairagarh-Chhuikhadan-Gandai", "Kondagaon", "Korba", "Korea",
        "Mahasamund", "Manendragarh-Chirmiri-Bharatpur(M C B)",
        "Mohla-Manpur-Ambagarh Chouki", "Mungeli", "Narayanpur", "Raigarh",
    ],
    "Dadra and Nagar Haveli and Daman and Diu": [
        "Dadra And Nagar Haveli", "Daman", "Diu",
    ],
    "Delhi": [
        "Central", "East", "New Delhi", "North", "North East", "North West",
        "Shahdara", "South", "South East", "South West", "West",
    ],
    "Goa": ["Kushavati", "North Goa", "South Goa"],
    "Gujarat": [
        "Ahmedabad", "Amreli", "Anand", "Arvalli", "Banas Kantha", "Bharuch",
        "Bhavnagar", "Botad", "Chhotaudepur", "Dahod", "Dangs",
        "Devbhumi Dwarka", "Gandhinagar", "Gir Somnath", "Jamnagar",
        "Junagadh", "Kachchh", "Kheda", "Mahesana", "Mahisagar", "Morbi",
        "Narmada", "Navsari", "Panch Mahals", "Patan",
    ],
    "Haryana": [
        "Ambala", "Bhiwani", "Charkhi Dadri", "Faridabad", "Fatehabad",
        "Gurugram", "Hansi", "Hisar", "Jhajjar", "Jind", "Kaithal", "Karnal",
        "Kurukshetra", "Mahendragarh", "Nuh", "Palwal", "Panchkula",
        "Panipat", "Rewari", "Rohtak", "Sirsa", "Sonipat", "Yamunanagar",
    ],
    "Himachal Pradesh": [
        "Bilaspur", "Chamba", "Hamirpur", "Kangra", "Kinnaur", "Kullu",
        "Lahaul And Spiti", "Mandi", "Shimla", "Sirmaur", "Solan", "Una",
    ],
    "Jammu and Kashmir": [
        "Anantnag", "Bandipora", "Baramulla", "Budgam", "Doda", "Ganderbal",
        "Jammu", "Kathua", "Kishtwar", "Kulgam", "Kupwara", "Poonch",
        "Pulwama", "Rajouri", "Ramban", "Reasi", "Samba", "Shopian",
        "Srinagar", "Udhampur",
    ],
    "Jharkhand": [
        "Bokaro", "Chatra", "Deoghar", "Dhanbad", "Dumka", "East Singhbum",
        "Garhwa", "Giridih", "Godda", "Gumla", "Hazaribagh", "Jamtara",
        "Khunti", "Koderma", "Latehar", "Lohardaga", "Pakur", "Palamu",
        "Ramgarh", "Ranchi", "Sahebganj", "Saraikela Kharsawan", "Simdega",
        "West Singhbhum",
    ],
    "Karnataka": [
        "Bagalkote", "Ballari", "Belagavi", "Bengaluru Rural",
        "Bengaluru South", "Bengaluru Urban", "Bidar", "Chamarajanagar",
        "Chikkaballapura", "Chikkamagaluru", "Chitradurga",
        "Dakshina Kannada", "Davanagere", "Dharwad", "Gadag", "Hassan",
        "Haveri", "Kalaburagi", "Kodagu", "Kolar", "Koppal", "Mandya",
        "Mysuru", "Raichur", "Shivamogga",
    ],
    "Kerala": [
        "Alappuzha", "Ernakulam", "Idukki", "Kannur", "Kasaragod", "Kollam",
        "Kottayam", "Kozhikode", "Malappuram", "Palakkad", "Pathanamthitta",
        "Thiruvananthapuram", "Thrissur", "Wayanad",
    ],
    "Ladakh": ["Kargil", "Leh Ladakh"],
    "Lakshadweep": ["Lakshadweep District"],
    "Madhya Pradesh": [
        "Agar-Malwa", "Alirajpur", "Anuppur", "Ashoknagar", "Balaghat",
        "Barwani", "Betul", "Bhind", "Bhopal", "Burhanpur", "Chhatarpur",
        "Chhindwara", "Damoh", "Datia", "Dewas", "Dhar", "Dindori", "Guna",
        "Gwalior", "Harda", "Indore", "Jabalpur", "Jhabua", "Katni",
        "Khandwa (East Nimar)",
    ],
    "Maharashtra": [
        "Ahilyanagar", "Akola", "Amravati", "Beed", "Bhandara", "Buldhana",
        "Chandrapur", "Chhatrapati Sambhajinagar", "Dharashiv", "Dhule",
        "Gadchiroli", "Gondia", "Hingoli", "Jalgaon", "Jalna", "Kolhapur",
        "Latur", "Mumbai", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar",
        "Nashik", "Palghar", "Parbhani",
    ],
    "Manipur": [
        "Bishnupur", "Chandel", "Churachandpur", "Imphal East", "Imphal West",
        "Jiribam", "Kakching", "Kamjong", "Kangpokpi", "Noney", "Pherzawl",
        "Senapati", "Tamenglong", "Tengnoupal", "Thoubal", "Ukhrul",
    ],
    "Meghalaya": [
        "East Garo Hills", "East Jaintia Hills", "East Khasi Hills",
        "Eastern West Khasi Hills", "North Garo Hills", "Ri Bhoi",
        "South Garo Hills", "South West Garo Hills", "South West Khasi Hills",
        "West Garo Hills", "West Jaintia Hills", "West Khasi Hills",
    ],
    "Mizoram": [
        "Aizawl", "Champhai", "Hnahthial", "Khawzawl", "Kolasib",
        "Lawngtlai", "Lunglei", "Mamit", "Saitual", "Serchhip", "Siaha",
    ],
    "Nagaland": [
        "Chumoukedima", "Dimapur", "Kiphire", "Kohima", "Longleng", "Meluri",
        "Mokokchung", "Mon", "Niuland", "Noklak", "Peren", "Phek",
        "Shamator", "Tseminyu", "Tuensang", "Wokha", "Zunheboto",
    ],
    "Odisha": [
        "Angul", "Balangir", "Balasore", "Bargarh", "Bhadrak", "Boudh",
        "Cuttack", "Deogarh", "Dhenkanal", "Gajapati", "Ganjam",
        "Jagatsinghapur", "Jajpur", "Jharsuguda", "Kalahandi", "Kandhamal",
        "Kendrapara", "Keonjhar", "Khordha", "Koraput", "Malkangiri",
        "Mayurbhanj", "Nabarangpur", "Nayagarh", "Nuapada",
    ],
    "Puducherry": ["Karaikal", "Puducherry"],
    "Punjab": [
        "Amritsar", "Barnala", "Bathinda", "Faridkot", "Fatehgarh Sahib",
        "Fazilka", "Ferozepur", "Gurdaspur", "Hoshiarpur", "Jalandhar",
        "Kapurthala", "Ludhiana", "Malerkotla", "Mansa", "Moga", "Pathankot",
        "Patiala", "Rupnagar", "S.A.S Nagar", "Sangrur",
        "Shahid Bhagat Singh Nagar", "Sri Muktsar Sahib", "Tarn Taran",
    ],
    "Rajasthan": [
        "Ajmer", "Alwar", "Balotra", "Banswara", "Baran", "Barmer", "Beawar",
        "Bharatpur", "Bhilwara", "Bikaner", "Bundi", "Chittorgarh", "Churu",
        "Dausa", "Deeg", "Dholpur", "Didwana-Kuchaman", "Dungarpur",
        "Ganganagar", "Hanumangarh", "Jaipur", "Jaisalmer", "Jalore",
        "Jhalawar", "Jhunjhunu",
    ],
    "Sikkim": ["Gangtok", "Gyalshing", "Mangan", "Namchi", "Pakyong", "Soreng"],
    "Tamil Nadu": [
        "Ariyalur", "Chengalpattu", "Chennai", "Coimbatore", "Cuddalore",
        "Dharmapuri", "Dindigul", "Erode", "Kallakurichi", "Kancheepuram",
        "Kanniyakumari", "Karur", "Krishnagiri", "Madurai",
        "Mayiladuthurai", "Nagapattinam", "Namakkal", "Perambalur",
        "Pudukkottai", "Ramanathapuram", "Ranipet", "Salem", "Sivaganga",
        "Tenkasi", "Thanjavur",
    ],
    "Telangana": [
        "Adilabad", "Bhadradri Kothagudem", "Hanumakonda", "Hyderabad",
        "Jagitial", "Jangoan", "Jayashankar Bhupalapally",
        "Jogulamba Gadwal", "Kamareddy", "Karimnagar", "Khammam",
        "Kumuram Bheem Asifabad", "Mahabubabad", "Mahabubnagar",
        "Mancherial", "Medak", "Medchal Malkajgiri", "Mulugu",
        "Nagarkurnool", "Nalgonda", "Narayanpet", "Nirmal", "Nizamabad",
        "Peddapalli", "Rajanna Sircilla",
    ],
    "Tripura": [
        "Dhalai", "Gomati", "Khowai", "North Tripura", "Sepahijala",
        "South Tripura", "Unakoti", "West Tripura",
    ],
    "Uttar Pradesh": [
        "Agra", "Aligarh", "Ambedkar Nagar", "Amethi", "Amroha", "Auraiya",
        "Ayodhya", "Azamgarh", "Baghpat", "Bahraich", "Ballia", "Balrampur",
        "Banda", "Bara Banki", "Bareilly", "Basti", "Bhadohi", "Bijnor",
        "Budaun", "Bulandshahr", "Chandauli", "Chitrakoot", "Deoria", "Etah",
        "Etawah",
    ],
    "Uttarakhand": [
        "Almora", "Bageshwar", "Chamoli", "Champawat", "Dehradun",
        "Haridwar", "Nainital", "Pauri Garhwal", "Pithoragarh",
        "Rudraprayag", "Tehri Garhwal", "Udham Singh Nagar", "Uttarkashi",
    ],
    "West Bengal": [
        "Alipurduar", "Bankura", "Birbhum", "Cooch Behar",
        "Dakshin Dinajpur", "Darjeeling", "Hooghly", "Howrah", "Jalpaiguri",
        "Jhargram", "Kalimpong", "Kolkata", "Malda", "Murshidabad", "Nadia",
        "North 24 Parganas", "Paschim Bardhaman", "Paschim Medinipur",
        "Purba Bardhaman", "Purba Medinipur", "Purulia", "South 24 Parganas",
        "Uttar Dinajpur",
    ],
}

def seed():
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS districts")
    cursor.execute("""
        CREATE TABLE districts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (state_id) REFERENCES states(id),
            UNIQUE(state_id, name)
        )
    """)

    total = 0
    for state_name, dists in STATE_DISTRICTS.items():
        cursor.execute("SELECT id FROM states WHERE name = ?", (state_name,))
        row = cursor.fetchone()
        if not row:
            print(f"  State '{state_name}' not found, skipping")
            continue
        state_id = row[0]
        for dist in dists:
            cursor.execute(
                "INSERT OR IGNORE INTO districts (state_id, name) VALUES (?, ?)",
                (state_id, dist),
            )
        total += len(dists)

    conn.commit()
    conn.close()
    print(f"Seeded {total} districts across {len(STATE_DISTRICTS)} states.")

if __name__ == "__main__":
    seed()
