"""
TripWise — Destination Places Data
====================================
Stores tourist place data keyed by normalized destination name.
The nearby attraction helper can use Google Places when an API key is configured,
while retaining a rich in-app fallback for local demo and offline behavior.
"""

import os
import urllib.request
import urllib.parse
import json

# ---------------------------------------------------------------------------
# Data Store
# ---------------------------------------------------------------------------
DESTINATION_PLACES = {
    "goa": [
        {
            "id": "goa_1",
            "name": "Baga Beach",
            "description": "One of Goa's most popular beaches, Baga is famous for its vibrant nightlife, water sports, and shacks serving fresh seafood. The golden sands stretch for miles with a lively, festive atmosphere.",
            "best_time": "October – March",
            "duration": "2–4 hours",
            "category": "Beach",
            "time_of_day": ["Morning", "Evening"],
            "travel_type": ["Family", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=600&auto=format&fit=crop",
        },
        {
            "id": "goa_2",
            "name": "Calangute Beach",
            "description": "Known as the 'Queen of Beaches', Calangute is the largest beach in North Goa. It offers a perfect blend of water sports, beach shacks, and a bustling bazaar just steps away.",
            "best_time": "November – February",
            "duration": "3–5 hours",
            "category": "Beach",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=600&auto=format&fit=crop",
        },
        {
            "id": "goa_3",
            "name": "Fort Aguada",
            "description": "A 17th-century Portuguese fort perched on the Arabian Sea coast. Fort Aguada offers panoramic ocean views, a historic lighthouse, and a fascinating glimpse into Goa's colonial past.",
            "best_time": "October – April",
            "duration": "2–3 hours",
            "category": "Historical",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&auto=format&fit=crop",
        },
        {
            "id": "goa_4",
            "name": "Dudhsagar Falls",
            "description": "One of India's tallest waterfalls at 310 meters, Dudhsagar (Sea of Milk) cascades through lush rainforest in the Western Ghats. Reachable by jeep safari through Bhagwan Mahavir Wildlife Sanctuary.",
            "best_time": "June – September (monsoon), November – February",
            "duration": "Full day (6–8 hours with travel)",
            "category": "Nature",
            "time_of_day": ["Morning"],
            "travel_type": ["Adventure", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=600&auto=format&fit=crop",
        },
        {
            "id": "goa_5",
            "name": "Basilica of Bom Jesus",
            "description": "A UNESCO World Heritage Site, this 16th-century baroque church houses the mortal remains of St. Francis Xavier. One of the oldest and finest churches in India, a must-visit for history lovers.",
            "best_time": "October – March",
            "duration": "1–2 hours",
            "category": "Temple",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1571930068971-a1e66b9abeab?w=600&auto=format&fit=crop",
        },
        {
            "id": "goa_6",
            "name": "Palolem Beach",
            "description": "A crescent-shaped beach in South Goa, Palolem is known for its calm, crystal-clear waters, stunning sunsets, and a quieter, more laid-back vibe compared to North Goa beaches.",
            "best_time": "November – March",
            "duration": "3–5 hours",
            "category": "Beach",
            "time_of_day": ["Afternoon", "Evening"],
            "travel_type": ["Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&auto=format&fit=crop",
        },
        {
            "id": "goa_7",
            "name": "Chapora Fort",
            "description": "Immortalised by the Bollywood movie Dil Chahta Hai, Chapora Fort overlooks the Vagator Beach. The ruins provide spectacular views of the coastline and the winding Chapora River.",
            "best_time": "October – March",
            "duration": "1–2 hours",
            "category": "Historical",
            "time_of_day": ["Morning", "Evening"],
            "travel_type": ["Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1563720223523-91ab0a45a9e7?w=600&auto=format&fit=crop",
        },
        {
            "id": "goa_8",
            "name": "Anjuna Flea Market",
            "description": "Held every Wednesday, this iconic market is a treasure trove of handicrafts, jewellery, spices, and unique souvenirs. It's the best place to soak in Goa's bohemian culture.",
            "best_time": "November – March (Wednesdays only)",
            "duration": "2–4 hours",
            "category": "Museum",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&auto=format&fit=crop",
        },
        {
            "id": "goa_9",
            "name": "Scuba Diving at Grand Island",
            "description": "Grand Island off the Goa coast is a hotspot for scuba diving and snorkelling. Discover vibrant coral reefs, shipwrecks, and an array of tropical marine life in the clear Arabian Sea.",
            "best_time": "October – May",
            "duration": "4–6 hours",
            "category": "Adventure",
            "time_of_day": ["Morning"],
            "travel_type": ["Adventure", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1596464716127-f2a82984de30?w=600&auto=format&fit=crop",
        },
        {
            "id": "goa_10",
            "name": "Spice Plantation Tour",
            "description": "Explore lush spice plantations in Goa's interior, learn about exotic spices like cardamom, pepper, and vanilla, and enjoy a traditional Goan lunch in a scenic natural setting.",
            "best_time": "October – May",
            "duration": "3–4 hours",
            "category": "Nature",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop",
        },
    ],

    "jaipur": [
        {
            "id": "jpr_1",
            "name": "Amber Fort",
            "description": "A magnificent hilltop fort built in the 16th century by Raja Man Singh, Amber Fort is a blend of Hindu and Mughal architecture. Elephant rides to the entrance gate are an iconic experience.",
            "best_time": "October – March",
            "duration": "3–4 hours",
            "category": "Fort",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&auto=format&fit=crop",
        },
        {
            "id": "jpr_2",
            "name": "Hawa Mahal",
            "description": "The iconic 'Palace of Winds' features 953 small windows with intricate latticework, built so royal ladies could observe street festivals without being seen. A symbol of Jaipur's royal heritage.",
            "best_time": "October – March",
            "duration": "1–2 hours",
            "category": "Historical",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1477587458883-47145ed31fd8?w=600&auto=format&fit=crop",
        },
        {
            "id": "jpr_3",
            "name": "City Palace",
            "description": "A stunning royal complex in the heart of Jaipur, the City Palace houses museums, courtyards, and the Chandra Mahal — still the residence of the royal family — with impressive Rajput-Mughal architecture.",
            "best_time": "October – March",
            "duration": "2–3 hours",
            "category": "Historical",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?w=600&auto=format&fit=crop",
        },
        {
            "id": "jpr_4",
            "name": "Jantar Mantar",
            "description": "A UNESCO World Heritage Site, Jantar Mantar is an 18th-century astronomical observatory with 19 major geometric devices for measuring time, predicting eclipses, and tracking star locations.",
            "best_time": "October – February",
            "duration": "1–2 hours",
            "category": "Museum",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=600&auto=format&fit=crop",
        },
        {
            "id": "jpr_5",
            "name": "Nahargarh Fort",
            "description": "Perched on the Aravalli Hills, Nahargarh Fort offers the most spectacular panoramic view of Jaipur city. The sunset views are particularly magical, perfect for photography enthusiasts.",
            "best_time": "October – March",
            "duration": "2–3 hours",
            "category": "Fort",
            "time_of_day": ["Afternoon", "Evening"],
            "travel_type": ["Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?w=600&auto=format&fit=crop",
        },
        {
            "id": "jpr_6",
            "name": "Jal Mahal",
            "description": "The 'Water Palace' appears to float in the middle of Man Sagar Lake, illuminated beautifully at night. A stunning photo opportunity, especially at sunset with the Aravalli Hills as a backdrop.",
            "best_time": "October – March",
            "duration": "1 hour",
            "category": "Historical",
            "time_of_day": ["Evening"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=600&auto=format&fit=crop",
        },
        {
            "id": "jpr_7",
            "name": "Johari Bazaar",
            "description": "Jaipur's famous jewellery and handicraft market is a shopper's paradise. Browse through stunning Kundan and Meenakari jewellery, colourful bangles, and traditional Rajasthani textiles.",
            "best_time": "November – February",
            "duration": "2–3 hours",
            "category": "Museum",
            "time_of_day": ["Afternoon"],
            "travel_type": ["Family", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1539635278303-d4002c07eae3?w=600&auto=format&fit=crop",
        },
        {
            "id": "jpr_8",
            "name": "Albert Hall Museum",
            "description": "The oldest museum in Rajasthan, housed in a stunning Indo-Saracenic building, displays an eclectic collection of paintings, ivory, crystal, weapons, and an Egyptian mummy.",
            "best_time": "October – March",
            "duration": "2 hours",
            "category": "Museum",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1565534517-f2a81a63f98f?w=600&auto=format&fit=crop",
        },
    ],

    "manali": [
        {
            "id": "mnl_1",
            "name": "Rohtang Pass",
            "description": "A high mountain pass at 3,978 m on the Kullu-Lahaul-Spiti border, Rohtang offers breathtaking snow-capped peaks, glaciers, and thrilling adventure activities including skiing and snowboarding.",
            "best_time": "May – June, September – October",
            "duration": "Full day",
            "category": "Adventure",
            "time_of_day": ["Morning"],
            "travel_type": ["Adventure", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600&auto=format&fit=crop",
        },
        {
            "id": "mnl_2",
            "name": "Hadimba Temple",
            "description": "A unique cave temple dedicated to the goddess Hadimba, set amidst towering deodar cedar trees. The 16th-century wooden pagoda-style temple is one of the most photographed spots in Manali.",
            "best_time": "March – June, September – December",
            "duration": "1–2 hours",
            "category": "Temple",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1622838320302-4b3b3b3b3b3b?w=600&auto=format&fit=crop",
        },
        {
            "id": "mnl_3",
            "name": "Solang Valley",
            "description": "A scenic valley 14 km from Manali, famous for adventure sports like zorbing, paragliding, horse riding, and skiing in winter. Stunning views of glaciers and snow-capped peaks.",
            "best_time": "December – February (snow sports), May – June (other activities)",
            "duration": "Half day",
            "category": "Adventure",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Adventure", "Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1531572753322-ad063cecc140?w=600&auto=format&fit=crop",
        },
        {
            "id": "mnl_4",
            "name": "Old Manali",
            "description": "A charming village above the main town, Old Manali is famous for its bohemian cafes, local apple orchards, and the ancient Manu Temple. Perfect for a leisurely evening stroll.",
            "best_time": "April – October",
            "duration": "2–3 hours",
            "category": "Nature",
            "time_of_day": ["Afternoon", "Evening"],
            "travel_type": ["Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1626015365107-39e78eb79a8d?w=600&auto=format&fit=crop",
        },
        {
            "id": "mnl_5",
            "name": "Beas River Rafting",
            "description": "White-water rafting on the Beas River is one of Manali's most thrilling activities. Navigate through Grade II–III rapids surrounded by stunning mountain scenery for an unforgettable adventure.",
            "best_time": "July – October",
            "duration": "2–3 hours",
            "category": "Adventure",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Adventure", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1530789253388-582c481c54b0?w=600&auto=format&fit=crop",
        },
        {
            "id": "mnl_6",
            "name": "Naggar Castle",
            "description": "A 500-year-old stone-and-wood castle on the banks of the Beas River, now converted into a heritage hotel. The castle offers panoramic views of the Kullu Valley and houses an art gallery.",
            "best_time": "March – November",
            "duration": "2 hours",
            "category": "Historical",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1609766857385-20b5ea8e96ed?w=600&auto=format&fit=crop",
        },
        {
            "id": "mnl_7",
            "name": "Jogini Waterfall",
            "description": "A stunning 160-ft waterfall reached by a 2 km trek through apple orchards and pine forests. The trek itself offers spectacular views, and the cool pool at the base is perfect for a refreshing dip.",
            "best_time": "May – October",
            "duration": "3–4 hours (including trek)",
            "category": "Nature",
            "time_of_day": ["Morning"],
            "travel_type": ["Adventure", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=600&auto=format&fit=crop",
        },
        {
            "id": "mnl_8",
            "name": "Manikaran Sahib Gurudwara",
            "description": "A sacred Sikh and Hindu pilgrimage site near Kasol, famous for its hot springs where devotees believe a holy dip washes away sins. The langar (community meal) served here is heartwarming.",
            "best_time": "May – October",
            "duration": "2–3 hours",
            "category": "Temple",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1579613832125-5d34a13ffe2a?w=600&auto=format&fit=crop",
        },
    ],

    "udaipur": [
        {
            "id": "udp_1",
            "name": "City Palace",
            "description": "The largest palace complex in Rajasthan, built over 400 years by successive Maharanas. It overlooks Lake Pichola and houses museums, galleries, towers, and royal courtyards with stunning lake views.",
            "best_time": "October – March",
            "duration": "3–4 hours",
            "category": "Historical",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=600&auto=format&fit=crop",
        },
        {
            "id": "udp_2",
            "name": "Lake Pichola",
            "description": "An artificial freshwater lake created in 1362, Lake Pichola is the soul of Udaipur. Take a boat ride to the island palaces of Jag Mandir and the famous Lake Palace Hotel, especially magical at sunset.",
            "best_time": "October – March",
            "duration": "2–3 hours",
            "category": "Nature",
            "time_of_day": ["Evening"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&auto=format&fit=crop",
        },
        {
            "id": "udp_3",
            "name": "Jagdish Temple",
            "description": "A large Hindu temple built in 1651, dedicated to Lord Vishnu in the form of Jagannath. Known for its intricately carved pillars, detailed artwork, and continuous chanting that fills the air.",
            "best_time": "October – March",
            "duration": "1 hour",
            "category": "Temple",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1571930068971-a1e66b9abeab?w=600&auto=format&fit=crop",
        },
        {
            "id": "udp_4",
            "name": "Sajjangarh (Monsoon Palace)",
            "description": "Perched atop the Aravalli Hills, this white marble hilltop palace was built in 1884 to watch monsoon clouds. Now a wildlife sanctuary, it offers breathtaking 360° views of Udaipur city.",
            "best_time": "October – March",
            "duration": "2 hours",
            "category": "Historical",
            "time_of_day": ["Evening"],
            "travel_type": ["Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1477587458883-47145ed31fd8?w=600&auto=format&fit=crop",
        },
        {
            "id": "udp_5",
            "name": "Fateh Sagar Lake",
            "description": "An artificial lake north of the city, Fateh Sagar Lake has three islands — one with a public park, one with a solar observatory, and one with a water jet fountain. A peaceful evening retreat.",
            "best_time": "October – February",
            "duration": "1–2 hours",
            "category": "Nature",
            "time_of_day": ["Evening"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?w=600&auto=format&fit=crop",
        },
        {
            "id": "udp_6",
            "name": "Bagore Ki Haveli",
            "description": "An 18th-century haveli on the waterfront of Lake Pichola, with 138 rooms displaying Mewar costumes, puppets, and antique items. Evening cultural shows with folk dances are unmissable.",
            "best_time": "October – March",
            "duration": "2 hours",
            "category": "Museum",
            "time_of_day": ["Afternoon", "Evening"],
            "travel_type": ["Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1565534517-f2a81a63f98f?w=600&auto=format&fit=crop",
        },
        {
            "id": "udp_7",
            "name": "Saheliyon Ki Bari",
            "description": "The 'Garden of the Maidens', built for royal ladies in the 18th century. Features beautiful fountains, marble elephants, a lotus pool, and lush greenery — a serene oasis in the heart of the city.",
            "best_time": "October – March",
            "duration": "1 hour",
            "category": "Nature",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop",
        },
        {
            "id": "udp_8",
            "name": "Kumbhalgarh Fort",
            "description": "A UNESCO World Heritage Site 84 km from Udaipur, with the world's second-longest wall (36 km). The fort is set in lush forest and offers breathtaking views of the Aravalli Range.",
            "best_time": "October – March",
            "duration": "Full day (with travel)",
            "category": "Fort",
            "time_of_day": ["Morning"],
            "travel_type": ["Adventure", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=600&auto=format&fit=crop",
        },
    ],

    "agra": [
        {
            "id": "agr_1",
            "name": "Taj Mahal",
            "description": "One of the Seven Wonders of the World and a UNESCO Heritage Site, the Taj Mahal is an ivory-white marble mausoleum built by Emperor Shah Jahan in memory of his wife Mumtaz Mahal.",
            "best_time": "October – March (sunrise for best light)",
            "duration": "3–4 hours",
            "category": "Historical",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=600&auto=format&fit=crop",
        },
        {
            "id": "agr_2",
            "name": "Agra Fort",
            "description": "A massive red sandstone fort on the banks of the Yamuna, Agra Fort was the main residence of the Mughal dynasty. Its imposing walls hide palaces, mosques, and audience halls within.",
            "best_time": "October – March",
            "duration": "2–3 hours",
            "category": "Fort",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&auto=format&fit=crop",
        },
        {
            "id": "agr_3",
            "name": "Fatehpur Sikri",
            "description": "A UNESCO World Heritage Site 40 km from Agra, Fatehpur Sikri was the magnificent capital of the Mughal Empire briefly under Akbar. An exceptionally well-preserved ghost city of red sandstone.",
            "best_time": "October – March",
            "duration": "3–4 hours",
            "category": "Historical",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1477587458883-47145ed31fd8?w=600&auto=format&fit=crop",
        },
        {
            "id": "agr_4",
            "name": "Mehtab Bagh",
            "description": "A moonlit garden directly across the Yamuna from the Taj Mahal, offering the most iconic reflection view of the Taj at sunrise and sunset. A photographer's paradise with very few crowds.",
            "best_time": "October – March (sunset/sunrise)",
            "duration": "1–2 hours",
            "category": "Nature",
            "time_of_day": ["Morning", "Evening"],
            "travel_type": ["Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?w=600&auto=format&fit=crop",
        },
    ],

    "delhi": [
        {
            "id": "del_1",
            "name": "Red Fort",
            "description": "The majestic Red Fort, built by Emperor Shah Jahan in 1638, served as the main residence of the Mughal Emperors for nearly 200 years. Its massive red sandstone walls stretch for 2.4 km.",
            "best_time": "October – March",
            "duration": "2–3 hours",
            "category": "Fort",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?w=600&auto=format&fit=crop",
        },
        {
            "id": "del_2",
            "name": "Qutub Minar",
            "description": "The world's tallest brick minaret at 72.5 meters, Qutub Minar is a UNESCO World Heritage Site dating to 1193. The surrounding complex includes remarkable examples of early Afghan architecture.",
            "best_time": "October – March",
            "duration": "2 hours",
            "category": "Historical",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=600&auto=format&fit=crop",
        },
        {
            "id": "del_3",
            "name": "India Gate",
            "description": "A 42-meter-tall war memorial erected in honour of 70,000 Indian soldiers who died in World War I. The eternal flame burning beneath it is a poignant national symbol.",
            "best_time": "October – March (evenings)",
            "duration": "1–2 hours",
            "category": "Historical",
            "time_of_day": ["Evening"],
            "travel_type": ["Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=600&auto=format&fit=crop",
        },
        {
            "id": "del_4",
            "name": "Humayun's Tomb",
            "description": "A UNESCO World Heritage Site and predecessor to the Taj Mahal, Humayun's Tomb was the first garden-tomb in India. Its Persian-influenced architecture inspired many later Mughal masterpieces.",
            "best_time": "October – March",
            "duration": "2 hours",
            "category": "Historical",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1477587458883-47145ed31fd8?w=600&auto=format&fit=crop",
        },
        {
            "id": "del_5",
            "name": "Lotus Temple",
            "description": "An architectural marvel built in the shape of a half-open lotus flower, this Bahá'í House of Worship welcomes people of all religions for quiet prayer and meditation. No sermons, no rituals.",
            "best_time": "October – March",
            "duration": "1 hour",
            "category": "Temple",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1571930068971-a1e66b9abeab?w=600&auto=format&fit=crop",
        },
        {
            "id": "del_6",
            "name": "Chandni Chowk",
            "description": "One of the oldest and busiest markets in Old Delhi, Chandni Chowk is a sensory explosion of narrow lanes, spice shops, street food stalls, and colourful bazaars — a true slice of Mughal-era India.",
            "best_time": "October – March (mornings)",
            "duration": "3 hours",
            "category": "Museum",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1539635278303-d4002c07eae3?w=600&auto=format&fit=crop",
        },
    ],

    "kerala": [
        {
            "id": "ker_1",
            "name": "Alleppey Backwaters",
            "description": "A network of lakes, canals, and lagoons running parallel to the Arabian Sea coast, Alleppey's backwaters are best explored on a traditional houseboat with a chef, gliding through serene village life.",
            "best_time": "November – February",
            "duration": "Full day or overnight",
            "category": "Nature",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=600&auto=format&fit=crop",
        },
        {
            "id": "ker_2",
            "name": "Munnar Tea Gardens",
            "description": "Sprawling green tea plantations cover the rolling hills of Munnar at 1,600m elevation. The misty mountains, cool climate, and scenic drives make it one of India's most stunning hill stations.",
            "best_time": "September – May",
            "duration": "Full day",
            "category": "Nature",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=600&auto=format&fit=crop",
        },
        {
            "id": "ker_3",
            "name": "Periyar Wildlife Sanctuary",
            "description": "Nestled around Periyar Lake at Thekkady, this sanctuary is home to elephants, tigers, leopards, and diverse bird species. Boat safaris on the lake for wildlife spotting are unforgettable.",
            "best_time": "September – April",
            "duration": "Half day",
            "category": "Nature",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Adventure", "Group"],
            "image_url": "https://images.unsplash.com/photo-1580502304784-8985b7eb7260?w=600&auto=format&fit=crop",
        },
        {
            "id": "ker_4",
            "name": "Kovalam Beach",
            "description": "A crescent-shaped beach 16 km from Thiruvananthapuram, Kovalam is Kerala's most famous beach with world-class Ayurvedic spas, surf schools, and a beautiful lighthouse at its southern tip.",
            "best_time": "November – February",
            "duration": "Half day",
            "category": "Beach",
            "time_of_day": ["Afternoon", "Evening"],
            "travel_type": ["Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=600&auto=format&fit=crop",
        },
    ],

    "rishikesh": [
        {
            "id": "rsh_1",
            "name": "Laxman Jhula",
            "description": "A famous iron suspension bridge built in 1939 over the Ganges River, Laxman Jhula is both a pilgrimage site and a popular viewpoint. The vibrant ghats and temples around it create a magical atmosphere.",
            "best_time": "September – June",
            "duration": "1–2 hours",
            "category": "Temple",
            "time_of_day": ["Morning", "Evening"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1561361058-c24cecae35ca?w=600&auto=format&fit=crop",
        },
        {
            "id": "rsh_2",
            "name": "Ganga Aarti at Triveni Ghat",
            "description": "A magnificent evening ritual at Triveni Ghat, where priests perform synchronized aarti (prayer ceremony) with massive fire lamps to the Ganges River. An incredibly spiritual experience.",
            "best_time": "Year-round (evenings at 6 PM)",
            "duration": "1–2 hours",
            "category": "Temple",
            "time_of_day": ["Evening"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600&auto=format&fit=crop",
        },
        {
            "id": "rsh_3",
            "name": "White Water Rafting on Ganga",
            "description": "One of India's most thrilling rafting experiences, navigating Grade II–IV rapids on the Ganges through stunning gorges. Different routes available from 9 km to 26 km for all experience levels.",
            "best_time": "September – June",
            "duration": "3–6 hours",
            "category": "Adventure",
            "time_of_day": ["Morning"],
            "travel_type": ["Adventure", "Group"],
            "image_url": "https://images.unsplash.com/photo-1530789253388-582c481c54b0?w=600&auto=format&fit=crop",
        },
        {
            "id": "rsh_4",
            "name": "Beatles Ashram (Chaurasi Kutia)",
            "description": "The ashram where the Beatles stayed in 1968 to learn Transcendental Meditation is now an open-air art gallery within a forest. The colourful murals and ruins create an ethereal, creative atmosphere.",
            "best_time": "September – June",
            "duration": "2 hours",
            "category": "Historical",
            "time_of_day": ["Morning"],
            "travel_type": ["Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1626015365107-39e78eb79a8d?w=600&auto=format&fit=crop",
        },
        {
            "id": "rsh_5",
            "name": "Neer Garh Waterfall",
            "description": "A beautiful series of tiered waterfalls 3 km from Rishikesh, reached by a pleasant forest trek. Surrounded by lush vegetation, it's a perfect escape from the town's hustle.",
            "best_time": "July – February",
            "duration": "3 hours (including trek)",
            "category": "Nature",
            "time_of_day": ["Morning"],
            "travel_type": ["Adventure", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?w=600&auto=format&fit=crop",
        },
    ],

    "varanasi": [
        {
            "id": "var_1",
            "name": "Dashashwamedh Ghat",
            "description": "The main ghat on the Ganges and one of the most sacred in Hinduism, Dashashwamedh is famous for its spectacular Ganga Aarti ceremony every evening, attracting thousands of devotees and tourists.",
            "best_time": "October – March",
            "duration": "2–3 hours",
            "category": "Temple",
            "time_of_day": ["Evening"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=600&auto=format&fit=crop",
        },
        {
            "id": "var_2",
            "name": "Kashi Vishwanath Temple",
            "description": "One of the most famous Hindu temples dedicated to Lord Shiva and the most sacred of all Shiva temples, the Kashi Vishwanath is the heart of Varanasi, attracting millions of pilgrims annually.",
            "best_time": "October – March",
            "duration": "2 hours",
            "category": "Temple",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1571930068971-a1e66b9abeab?w=600&auto=format&fit=crop",
        },
        {
            "id": "var_3",
            "name": "Morning Boat Ride on the Ganges",
            "description": "A sunrise boat ride on the Ganges is one of the most profound experiences in India. Watch the city wake up from the river, see rituals at the ghats, and witness the cycle of life and death.",
            "best_time": "October – March (sunrise)",
            "duration": "2 hours",
            "category": "Nature",
            "time_of_day": ["Morning"],
            "travel_type": ["Solo", "Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1561361058-c24cecae35ca?w=600&auto=format&fit=crop",
        },
        {
            "id": "var_4",
            "name": "Sarnath",
            "description": "A major Buddhist pilgrimage centre 10 km from Varanasi, where Buddha delivered his first sermon after enlightenment. The Dhamek Stupa (5th century AD) and the Archaeological Museum are highlights.",
            "best_time": "October – March",
            "duration": "Half day",
            "category": "Historical",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1565534517-f2a81a63f98f?w=600&auto=format&fit=crop",
        },
    ],

    "mysore": [
        {
            "id": "mys_1",
            "name": "Mysore Palace",
            "description": "One of the most visited monuments in India (after the Taj Mahal), this Indo-Saracenic palace is a magnificent blend of Hindu, Muslim, Rajput, and Gothic architecture. Sunday evening illuminations are magical.",
            "best_time": "October – February",
            "duration": "2–3 hours",
            "category": "Historical",
            "time_of_day": ["Morning", "Evening"],
            "travel_type": ["Family", "Group", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?w=600&auto=format&fit=crop",
        },
        {
            "id": "mys_2",
            "name": "Chamundi Hills",
            "description": "A hill 13 km from Mysore city, topped by the magnificent Sri Chamundeshwari Temple. The 1,000-step climb passes a massive Nandi bull statue and rewards you with panoramic city views.",
            "best_time": "October – March",
            "duration": "2–3 hours",
            "category": "Temple",
            "time_of_day": ["Morning"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1526778548025-fa2f459cd5c1?w=600&auto=format&fit=crop",
        },
        {
            "id": "mys_3",
            "name": "Brindavan Gardens",
            "description": "Terraced gardens of the KRS Dam built in 1927, famous for their musical fountain show in the evenings with coloured lights. Over 150 varieties of plants are spread across the beautifully landscaped grounds.",
            "best_time": "October – February (evenings)",
            "duration": "2–3 hours",
            "category": "Nature",
            "time_of_day": ["Evening"],
            "travel_type": ["Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop",
        },
    ],
}


# ---------------------------------------------------------------------------
# Destination Overview Metadata (for hub banner + overview cards)
# ---------------------------------------------------------------------------
DESTINATION_INFO = {
    "goa": {
        "image_url": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1400&auto=format&fit=crop",
        "description": "India's smallest state packs a powerful punch — golden beaches, Portuguese heritage, spice-scented bazaars, and legendary nightlife make Goa one of Asia's most beloved destinations.",
        "best_time": "October – March",
        "known_for": ["Beach Life", "Water Sports", "Nightlife", "Seafood", "Portuguese Forts"],
    },
    "jaipur": {
        "image_url": "https://images.unsplash.com/photo-1477587458883-47145ed31fd8?w=1400&auto=format&fit=crop",
        "description": "The Pink City of Rajasthan dazzles with magnificent forts, opulent palaces, vibrant bazaars, and rich Rajputana heritage — a city where history lives and breathes at every corner.",
        "best_time": "October – March",
        "known_for": ["Royal Palaces", "Mughal Forts", "Handicrafts", "Rajasthani Cuisine", "Elephant Rides"],
    },
    "manali": {
        "image_url": "https://images.unsplash.com/photo-1626015365107-39e78eb79a8d?w=1400&auto=format&fit=crop",
        "description": "A high-altitude Himalayan resort town, Manali offers snow-capped mountains, adventure sports, lush valleys, and a gateway to the mystical Lahaul-Spiti trans-Himalayan plateau.",
        "best_time": "March – June, September – November",
        "known_for": ["Snow Treks", "Skiing", "River Rafting", "Mountain Views", "Adventure Sports"],
    },
    "udaipur": {
        "image_url": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=1400&auto=format&fit=crop",
        "description": "The City of Lakes charms with serene lakes, marble palaces, and the romance of Rajputana royalty. Udaipur consistently ranks among the world's most beautiful cities.",
        "best_time": "September – March",
        "known_for": ["Lake Palaces", "Boat Rides", "Rajput Architecture", "Folk Art", "Royal Heritage"],
    },
    "agra": {
        "image_url": "https://images.unsplash.com/photo-1564507592333-c60657eea523?w=1400&auto=format&fit=crop",
        "description": "Home to one of the Seven Wonders of the World, Agra is synonymous with the iconic Taj Mahal — the city overflows with Mughal grandeur, red sandstone forts, and timeless romance.",
        "best_time": "October – March",
        "known_for": ["Taj Mahal", "Mughal Architecture", "Agra Fort", "Petha Sweets", "Marble Art"],
    },
    "delhi": {
        "image_url": "https://images.unsplash.com/photo-1548013146-72479768bada?w=1400&auto=format&fit=crop",
        "description": "India's capital is a city of contrasts — ancient monuments shoulder-to-shoulder with modern skyscrapers. From Mughal grandeur to street food paradise, Delhi overwhelms the senses.",
        "best_time": "October – March",
        "known_for": ["Historical Monuments", "Street Food", "Shopping Bazaars", "Museums", "Nightlife"],
    },
    "kerala": {
        "image_url": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?w=1400&auto=format&fit=crop",
        "description": "God's Own Country lives up to its name with tranquil backwaters, misty tea gardens, pristine beaches, lush wildlife sanctuaries, and the world-famous Ayurvedic healing tradition.",
        "best_time": "September – March",
        "known_for": ["Backwater Houseboats", "Tea Plantations", "Ayurveda", "Wildlife", "Beaches"],
    },
    "rishikesh": {
        "image_url": "https://images.unsplash.com/photo-1561361058-c24cecae35ca?w=1400&auto=format&fit=crop",
        "description": "The Yoga Capital of the World sits where the Ganges emerges from the Himalayas — a blend of spiritual depth with adrenaline thrills: river rafting, bungee jumping, and ashram retreats.",
        "best_time": "February – May, September – November",
        "known_for": ["White Water Rafting", "Yoga & Meditation", "Ganga Aarti", "Bungee Jumping", "Ashrams"],
    },
    "varanasi": {
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=1400&auto=format&fit=crop",
        "description": "One of the world's oldest continuously inhabited cities, Varanasi is the spiritual heart of India. The ghats of the Ganges witness an endless cycle of life, death, and transcendence.",
        "best_time": "October – March",
        "known_for": ["Ganga Ghats", "Aarti Ceremonies", "Buddhist Pilgrimage", "Silk Weaving", "Hindu Temples"],
    },
    "mysore": {
        "image_url": "https://images.unsplash.com/photo-1599661046827-dacff0c0f09a?w=1400&auto=format&fit=crop",
        "description": "The City of Palaces glitters with Wadiyar royal dynasty grandeur. Mysore's illuminated palace, fragrant sandalwood, vibrant Dasara festival, and silk sarees are world-famous.",
        "best_time": "October – February",
        "known_for": ["Mysore Palace", "Dasara Festival", "Silk Sarees", "Sandalwood", "Chamundi Hills"],
    },
}


# ---------------------------------------------------------------------------
# Lookup Helpers
# ---------------------------------------------------------------------------

def normalize_destination(destination: str) -> str:
    """Normalize a destination string to a lookup key."""
    return destination.strip().lower().split(",")[0].strip()


def _fallback_place_image(destination: str, category: str) -> str:
    fallback_map = {
        "Tourist Attractions": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600&auto=format&fit=crop",
        "Historical Places": "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=600&auto=format&fit=crop",
        "Museums": "https://images.unsplash.com/photo-1565534517-f2a81a63f98f?w=600&auto=format&fit=crop",
        "Parks": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop",
        "Beaches": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=600&auto=format&fit=crop",
        "Shopping": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&auto=format&fit=crop",
        "Restaurants": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600&auto=format&fit=crop",
    }
    return fallback_map.get(category, f"https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&auto=format&fit=crop")


def _normalize_place_record(place: dict, destination: str, index: int = 0) -> dict:
    name = place.get("name") or f"{destination.title()} Attraction"
    category = place.get("category") or "Tourist Attractions"
    rating = place.get("rating") or (4.3 + (index % 4) * 0.2)
    address = place.get("address") or f"Central {destination.title()}, India"
    description = place.get("description") or f"A standout stop in {destination.title()} known for its atmosphere, history, and memorable views."
    opening_status = place.get("opening_status") or "Hours vary"
    image_url = place.get("image_url") or _fallback_place_image(destination, category)
    distance = place.get("distance") or f"{(index + 1) * 1.2:.1f} km from city center"
    price = place.get("price")
    return {
        "id": place.get("id") or f"place_{index + 1}",
        "name": name,
        "description": description,
        "best_time": place.get("best_time") or "Year-round",
        "duration": place.get("duration") or "2–4 hours",
        "category": category,
        "rating": float(rating),
        "address": address,
        "opening_status": opening_status,
        "image_url": image_url,
        "distance": distance,
        "price": price,
    }


def get_nearby_attractions(destination: str) -> list:
    """Return attraction cards from local destination data."""
    destination = (destination or '').strip()
    if not destination:
        return []

    fallback_places = get_places(destination)
    return [_normalize_place_record(place, destination, idx) for idx, place in enumerate(fallback_places)]


def get_destination_info(destination: str) -> dict:
    """Return destination metadata, falling back to Wikipedia for unknown places."""
    key = normalize_destination(destination)
    if key in DESTINATION_INFO:
        return DESTINATION_INFO[key]
    
    # Fallback to Wikipedia API
    title = urllib.parse.quote(destination.title())
    url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts|pageimages&exintro&explaintext&titles={title}&format=json&pithumbsize=1400"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TripWiseApp/1.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode())
            pages = data.get("query", {}).get("pages", {})
            for page_id, page_info in pages.items():
                if page_id == "-1":
                    continue
                extract = page_info.get("extract", f"Explore the beautiful sights of {destination.title()}.")
                if len(extract) > 300:
                    extract = extract[:297] + "..."
                
                # Default generic travel image if wiki doesn't have one
                img_url = page_info.get("thumbnail", {}).get("source", "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1400&auto=format&fit=crop")
                
                return {
                    "image_url": img_url,
                    "description": extract,
                    "best_time": "Year-round",
                    "known_for": ["Culture", "History", "Local Cuisine", "Sightseeing", "Architecture"]
                }
    except Exception as e:
        pass

    return {
        "image_url": "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=1400&auto=format&fit=crop",
        "description": f"Discover the hidden gems, rich culture, and beautiful landscapes of {destination.title()}.",
        "best_time": "Year-round",
        "known_for": ["Culture", "History", "Local Cuisine", "Sightseeing", "Architecture"]
    }


def get_wikipedia_attractions(destination: str) -> list:
    """Fetch real attractions, real photos, and real descriptions from Wikipedia API for a destination."""
    destination_title = destination.title()
    search_query = f"{destination_title} tourist attractions"
    url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_query)}&format=json&utf8=1"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TripWiseApp/1.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            search_data = json.loads(response.read().decode())
            search_results = search_data.get("query", {}).get("search", [])[:8]
            
        if not search_results:
            return []
            
        places = []
        for index, item in enumerate(search_results):
            title = item.get("title")
            if title.lower() == destination.lower():
                continue
                
            details_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts|pageimages&exintro&explaintext&titles={urllib.parse.quote(title)}&pithumbsize=800&format=json"
            try:
                details_req = urllib.request.Request(details_url, headers={'User-Agent': 'TripWiseApp/1.0'})
                with urllib.request.urlopen(details_req, timeout=3) as details_response:
                    details_data = json.loads(details_response.read().decode())
                    pages = details_data.get("query", {}).get("pages", {})
                    for page_id, page_info in pages.items():
                        if page_id == "-1":
                            continue
                        extract = page_info.get("extract", "")
                        if not extract:
                            continue
                        if len(extract) > 200:
                            extract = extract[:197] + "..."
                        
                        img_url = page_info.get("thumbnail", {}).get("source")
                        if not img_url:
                            category_fallback = {
                                "Tourist Attractions": "https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=600&auto=format&fit=crop",
                                "Historical Places": "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=600&auto=format&fit=crop",
                                "Museums": "https://images.unsplash.com/photo-1565534517-f2a81a63f98f?w=600&auto=format&fit=crop",
                                "Parks": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop",
                                "Beaches": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=600&auto=format&fit=crop"
                            }
                            img_url = category_fallback.get("Tourist Attractions")
                        
                        category = "Tourist Attractions"
                        title_lower = title.lower()
                        if any(k in title_lower for k in ["museum", "gallery", "art"]):
                            category = "Museums"
                        elif any(k in title_lower for k in ["park", "garden", "nature", "forest", "lake", "river"]):
                            category = "Parks"
                        elif any(k in title_lower for k in ["beach", "sea", "bay", "island", "ocean"]):
                            category = "Beaches"
                        elif any(k in title_lower for k in ["fort", "castle", "palace", "history", "ancient", "ruins", "monument", "tomb", "temple", "church", "cathedral", "mosque"]):
                            category = "Historical Places"
                            
                        places.append({
                            "id": f"wiki_{page_id}",
                            "name": title,
                            "description": extract,
                            "best_time": "Year-round",
                            "duration": "2–3 hours",
                            "category": category,
                            "rating": 4.5 + (index % 5) * 0.1,
                            "address": f"{title}, {destination_title}",
                            "opening_status": "Open daily",
                            "image_url": img_url,
                            "maps_url": f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(title + ' ' + destination_title)}",
                            "distance": f"{(index + 1) * 0.8:.1f} km from city center",
                        })
            except Exception:
                continue
        return places
    except Exception:
        return []


def get_places(destination: str) -> list:
    """Return a list of tourist places, falling back to Wikipedia for real places first."""
    key = normalize_destination(destination)
    if key in DESTINATION_PLACES:
        return DESTINATION_PLACES[key]
    
    # Try fetching real attractions and photos from Wikipedia
    wiki_places = get_wikipedia_attractions(destination)
    if wiki_places:
        return wiki_places

    # Generate generic places for unknown destination
    dest_title = destination.title()

    return [
        {
            "id": f"{key}_1",
            "name": f"{dest_title} City Center",
            "description": f"The vibrant heart of {dest_title}, featuring local shops, historical architecture, and bustling cafes.",
            "best_time": "Year-round",
            "duration": "2–4 hours",
            "category": "Historical",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1519681393784-d120267933ba?w=600&auto=format&fit=crop",
        },
        {
            "id": f"{key}_2",
            "name": f"National Museum of {dest_title}",
            "description": f"Explore the rich history and cultural heritage of {dest_title} through fascinating exhibits and artifacts.",
            "best_time": "Year-round",
            "duration": "2–3 hours",
            "category": "Museum",
            "time_of_day": ["Morning", "Afternoon"],
            "travel_type": ["Family", "Solo"],
            "image_url": "https://images.unsplash.com/photo-1565534517-f2a81a63f98f?w=600&auto=format&fit=crop",
        },
        {
            "id": f"{key}_3",
            "name": f"{dest_title} Central Park",
            "description": f"A beautiful green oasis perfect for a relaxing stroll, picnics, and enjoying the natural beauty of {dest_title}.",
            "best_time": "Spring / Summer",
            "duration": "1–2 hours",
            "category": "Nature",
            "time_of_day": ["Morning", "Evening"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=600&auto=format&fit=crop",
        },
        {
            "id": f"{key}_4",
            "name": f"Grand {dest_title} Hotel",
            "description": f"Experience luxury and comfort in the heart of {dest_title} with world-class amenities.",
            "best_time": "Year-round",
            "duration": "Overnight",
            "category": "Hotel",
            "time_of_day": ["Morning", "Evening"],
            "travel_type": ["Family", "Solo", "Group"],
            "image_url": "https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600&auto=format&fit=crop",
        },
        {
            "id": f"{key}_5",
            "name": f"{dest_title} Grand Mall",
            "description": f"The ultimate shopping destination in {dest_title} featuring international brands and local boutiques.",
            "best_time": "Year-round",
            "duration": "2–4 hours",
            "category": "Shopping",
            "time_of_day": ["Afternoon", "Evening"],
            "travel_type": ["Family", "Group"],
            "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600&auto=format&fit=crop",
        }
    ]


def get_supported_destinations() -> list:
    """Return a sorted list of all supported destination names."""
    return sorted(DESTINATION_PLACES.keys())




