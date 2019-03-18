#!/usr/bin/env python

countries = [0, 1, 2, 3, 4, 5, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 611, 612, 
             613, 614, 615, 616, 617, 618, 619, 620, 7, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 
             92, 93, 94, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 
             965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 
             983, 984, 985, 986, 987, 988, 989, 9927, 9928, 9929, 9930, 9931, 9932, 9933, 9934, 9935, 
             9936, 9937, 9938, 9939, 9940, 9941, 9942, 9943, 9944, 9945, 9946, 9947, 9948, 9949, 9950, 
             9951, 9952, 9953, 9954, 9955, 9956, 9957, 9958, 9959, 9960, 9961, 9962, 9963, 9964, 9965, 
             9966, 9967, 9968, 9970, 9971, 9972, 9973, 9974, 9975, 9976, 9977, 9978, 9979, 9980, 9981, 
             9982, 9983, 9984, 9985, 9986, 9987, 9988, 9989, 99901, 99902, 99903, 99904, 99905, 99906, 
             99908, 99909, 99910, 99911, 99912, 99913, 99914, 99915, 99916, 99917, 99918, 99919, 99920, 
             99921, 99922, 99923, 99924, 99925, 99926, 99927, 99928, 99929, 99930, 99931, 99932, 99933, 
             99934, 99935, 99936, 99937, 99938, 99939, 99940, 99941, 99942, 99943, 99944, 99945, 99946, 
             99947, 99948, 99949, 99950, 99951, 99952, 99953, 99954, 99955, 99956, 99957, 99958, 99959, 
             99960, 99961, 99962, 99963, 99964, 99965, 99966, 99967, 99968, 99969]


gi = {}

for country in countries:
    gi[country] = {'text': '', 'pubrange': ''} 



gi[0]['text'] = "English language"
gi[0]['pubrange'] = "00-19;200-699;7000-8499;85000-89999;900000-949999;9500000-9999999"
        

gi[1]['text'] = "English language"
gi[1]['pubrange'] = "00-09;100-399;4000-5499;55000-86979;869800-998999;9990000-9999999"
        

gi[2]['text'] = "French language"
gi[2]['pubrange'] = "00-19;200-349;35000-39999;400-699;7000-8399;84000-89999;900000-949999;9500000-9999999"
        

gi[3]['text'] = "German language"
gi[3]['pubrange'] = "00-02;030-033;0340-0369;03700-03999;04-19;200-699;7000-8499;85000-89999;900000-949999;9500000-9539999;95400-96999;9700000-9899999;99000-99499;99500-99999"
        

gi[4]['text'] = "Japan"
gi[4]['pubrange'] = "00-19;200-699;7000-8499;85000-89999;900000-949999;9500000-9999999"
        

gi[5]['text'] = "Russian Federation and former USSR"
gi[5]['pubrange'] = "00-19;200-420;4210-4299;430-430;4310-4399;440-440;4410-4499;450-699;7000-8499;85000-89999;900000-909999;91000-91999;9200-9299;93000-94999;9500000-9500999;9501-9799;98000-98999;9900000-9909999;9910-9999"
        

gi[600]['text'] = "Iran"
gi[600]['pubrange'] = "00-09;100-499;5000-8999;90000-99999"
        

gi[601]['text'] = "Kazakhstan"
gi[601]['pubrange'] = "00-19;200-699;7000-7999;80000-84999;85-99"
        

gi[602]['text'] = "Indonesia"
gi[602]['pubrange'] = "00-18;19000-19999;200-749;7500-7999;8000-9499;95000-99999"
        

gi[603]['text'] = "Saudi Arabia"
gi[603]['pubrange'] = "00-04;05-49;500-799;8000-8999;90000-99999"
        

gi[604]['text'] = "Vietnam"
gi[604]['pubrange'] = "0-4;50-89;900-979;9800-9999"
        

gi[605]['text'] = "Turkey"
gi[605]['pubrange'] = "01-09;100-399;4000-5999;60000-89999;90-99"
        

gi[606]['text'] = "Romania"
gi[606]['pubrange'] = "0-0;10-49;500-799;8000-9199;92000-99999"
        

gi[607]['text'] = "Mexico"
gi[607]['pubrange'] = "00-39;400-749;7500-9499;95000-99999"
        

gi[608]['text'] = "Macedonia"
gi[608]['pubrange'] = "0-0;10-19;200-449;4500-6499;65000-69999;7-9"
        

gi[609]['text'] = "Lithuania"
gi[609]['pubrange'] = "00-39;400-799;8000-9499;95000-99999"
        

gi[611]['text'] = "Thailand"
gi[611]['pubrange'] = ""
        

gi[612]['text'] = "Peru"
gi[612]['pubrange'] = "00-29;300-399;4000-4499;45000-49999;50-99"
        

gi[613]['text'] = "Mauritius"
gi[613]['pubrange'] = "0-9"
        

gi[614]['text'] = "Lebanon"
gi[614]['pubrange'] = "00-39;400-799;8000-9499;95000-99999"
        

gi[615]['text'] = "Hungary"
gi[615]['pubrange'] = "00-09;100-499;5000-7999;80000-89999"
        

gi[616]['text'] = "Thailand"
gi[616]['pubrange'] = "00-19;200-699;7000-8999;90000-99999"
        

gi[617]['text'] = "Ukraine"
gi[617]['pubrange'] = "00-49;500-699;7000-8999;90000-99999"
        

gi[618]['text'] = "Greece"
gi[618]['pubrange'] = "00-19;200-499;5000-7999;80000-99999"
        

gi[619]['text'] = "Bulgaria"
gi[619]['pubrange'] = "00-14;150-699;7000-8999;90000-99999"
        

gi[620]['text'] = "Mauritius"
gi[620]['pubrange'] = "0-9"
        

gi[7]['text'] = "China, People's Republic"
gi[7]['pubrange'] = "00-09;100-499;5000-7999;80000-89999;900000-999999"
        

gi[80]['text'] = "Czech Republic and Slovakia"
gi[80]['pubrange'] = "00-19;200-699;7000-8499;85000-89999;900000-999999"
        

gi[81]['text'] = "India"
gi[81]['pubrange'] = "00-19;200-699;7000-8499;85000-89999;900000-999999"
        

gi[82]['text'] = "Norway"
gi[82]['pubrange'] = "00-19;200-699;7000-8999;90000-98999;990000-999999"
        

gi[83]['text'] = "Poland"
gi[83]['pubrange'] = "00-19;200-599;60000-69999;7000-8499;85000-89999;900000-999999"
        

gi[84]['text'] = "Spain"
gi[84]['pubrange'] = "00-13;140-149;15000-19999;200-699;7000-8499;85000-89999;9000-9199;920000-923999;92400-92999;930000-949999;95000-96999;9700-9999"
        

gi[85]['text'] = "Brazil"
gi[85]['pubrange'] = "00-19;200-599;60000-69999;7000-8499;85000-89999;900000-979999;98000-99999"
        

gi[86]['text'] = "Serbia and Montenegro"
gi[86]['pubrange'] = "00-29;300-599;6000-7999;80000-89999;900000-999999"
        

gi[87]['text'] = "Denmark"
gi[87]['pubrange'] = "00-29;400-649;7000-7999;85000-94999;970000-999999"
        

gi[88]['text'] = "Italy"
gi[88]['pubrange'] = "00-19;200-599;6000-8499;85000-89999;900000-909999;910-929;95000-99999"
        

gi[89]['text'] = "Korea, Republic"
gi[89]['pubrange'] = "00-24;250-549;5500-8499;85000-94999;950000-969999;97000-98999;990-999"
        

gi[90]['text'] = "Netherlands"
gi[90]['pubrange'] = "00-19;200-499;5000-6999;70000-79999;800000-849999;8500-8999;90-90;910000-939999;94-94;950000-999999"
        

gi[91]['text'] = "Sweden"
gi[91]['pubrange'] = "0-1;20-49;500-649;7000-7999;85000-94999;970000-999999"
        

gi[92]['text'] = "International NGO Publishers and EC Organizations"
gi[92]['pubrange'] = "0-5;60-79;800-899;9000-9499;95000-98999;990000-999999"
        

gi[93]['text'] = "India"
gi[93]['pubrange'] = "00-09;100-499;5000-7999;80000-94999;950000-999999"
        

gi[94]['text'] = "Netherlands"
gi[94]['pubrange'] = "000-599;6000-8999;90000-99999"
        

gi[950]['text'] = "Argentina"
gi[950]['pubrange'] = "00-49;500-899;9000-9899;99000-99999"
        

gi[951]['text'] = "Finland"
gi[951]['pubrange'] = "0-1;20-54;550-889;8900-9499;95000-99999"
        

gi[952]['text'] = "Finland"
gi[952]['pubrange'] = "00-19;200-499;5000-5999;60-65;6600-6699;67000-69999;7000-7999;80-94;9500-9899;99000-99999"
        

gi[953]['text'] = "Croatia"
gi[953]['pubrange'] = "0-0;10-14;150-509;51-54;55000-59999;6000-9499;95000-99999"
        

gi[954]['text'] = "Bulgaria"
gi[954]['pubrange'] = "00-28;2900-2999;300-799;8000-8999;90000-92999;9300-9999"
        

gi[955]['text'] = "Sri Lanka"
gi[955]['pubrange'] = "0000-1999;20-49;50000-54999;550-799;8000-9499;95000-99999"
        

gi[956]['text'] = "Chile"
gi[956]['pubrange'] = "00-19;200-699;7000-9999"
        

gi[957]['text'] = "Taiwan"
gi[957]['pubrange'] = "00-02;0300-0499;05-19;2000-2099;21-27;28000-30999;31-43;440-819;8200-9699;97000-99999"
        

gi[958]['text'] = "Colombia"
gi[958]['pubrange'] = "00-56;57000-59999;600-799;8000-9499;95000-99999"
        

gi[959]['text'] = "Cuba"
gi[959]['pubrange'] = "00-19;200-699;7000-8499;85000-99999"
        

gi[960]['text'] = "Greece"
gi[960]['pubrange'] = "00-19;200-659;6600-6899;690-699;7000-8499;85000-92999;93-93;9400-9799;98000-99999"
        

gi[961]['text'] = "Slovenia"
gi[961]['pubrange'] = "00-19;200-599;6000-8999;90000-94999"
        

gi[962]['text'] = "Hong Kong, China"
gi[962]['pubrange'] = "00-19;200-699;7000-8499;85000-86999;8700-8999;900-999"
        

gi[963]['text'] = "Hungary"
gi[963]['pubrange'] = "00-19;200-699;7000-8499;85000-89999;9000-9999"
        

gi[964]['text'] = "Iran"
gi[964]['pubrange'] = "00-14;150-249;2500-2999;300-549;5500-8999;90000-96999;970-989;9900-9999"
        

gi[965]['text'] = "Israel"
gi[965]['pubrange'] = "00-19;200-599;7000-7999;90000-99999"
        

gi[966]['text'] = "Ukraine"
gi[966]['pubrange'] = "00-14;1500-1699;170-199;2000-2999;300-699;7000-8999;90000-99999"
        

gi[967]['text'] = "Malaysia"
gi[967]['pubrange'] = "00-00;0100-0999;10000-19999;300-499;5000-5999;60-89;900-989;9900-9989;99900-99999"
        

gi[968]['text'] = "Mexico"
gi[968]['pubrange'] = "01-39;400-499;5000-7999;800-899;9000-9999"
        

gi[969]['text'] = "Pakistan"
gi[969]['pubrange'] = "0-1;20-39;400-799;8000-9999"
        

gi[970]['text'] = "Mexico"
gi[970]['pubrange'] = "01-59;600-899;9000-9099;91000-96999;9700-9999"
        

gi[971]['text'] = "Philippines"
gi[971]['pubrange'] = "000-015;0160-0199;02-02;0300-0599;06-09;10-49;500-849;8500-9099;91000-95999;9600-9699;97-98;9900-9999"
        

gi[972]['text'] = "Portugal"
gi[972]['pubrange'] = "0-1;20-54;550-799;8000-9499;95000-99999"
        

gi[973]['text'] = "Romania"
gi[973]['pubrange'] = "0-0;100-169;1700-1999;20-54;550-759;7600-8499;85000-88999;8900-9499;95000-99999"
        

gi[974]['text'] = "Thailand"
gi[974]['pubrange'] = "00-19;200-699;7000-8499;85000-89999;90000-94999;9500-9999"
        

gi[975]['text'] = "Turkey"
gi[975]['pubrange'] = "00000-01999;02-24;250-599;6000-9199;92000-98999;990-999"
        

gi[976]['text'] = "Caribbean Community"
gi[976]['pubrange'] = "0-3;40-59;600-799;8000-9499;95000-99999"
        

gi[977]['text'] = "Egypt"
gi[977]['pubrange'] = "00-19;200-499;5000-6999;700-999"
        

gi[978]['text'] = "Nigeria"
gi[978]['pubrange'] = "000-199;2000-2999;30000-79999;8000-8999;900-999"
        

gi[979]['text'] = "Indonesia"
gi[979]['pubrange'] = "000-099;1000-1499;15000-19999;20-29;3000-3999;400-799;8000-9499;95000-99999"
        

gi[980]['text'] = "Venezuela"
gi[980]['pubrange'] = "00-19;200-599;6000-9999"
        

gi[981]['text'] = "Singapore"
gi[981]['pubrange'] = "00-11;1200-1999;200-289;2900-9999"
        

gi[982]['text'] = "South Pacific"
gi[982]['pubrange'] = "00-09;100-699;70-89;9000-9799;98000-99999"
        

gi[983]['text'] = "Malaysia"
gi[983]['pubrange'] = "00-01;020-199;2000-3999;40000-44999;45-49;50-79;800-899;9000-9899;99000-99999"
        

gi[984]['text'] = "Bangladesh"
gi[984]['pubrange'] = "00-39;400-799;8000-8999;90000-99999"
        

gi[985]['text'] = "Belarus"
gi[985]['pubrange'] = "00-39;400-599;6000-8999;90000-99999"
        

gi[986]['text'] = "Taiwan"
gi[986]['pubrange'] = "00-11;120-559;5600-7999;80000-99999"
        

gi[987]['text'] = "Argentina"
gi[987]['pubrange'] = "00-09;1000-1999;20000-29999;30-49;500-899;9000-9499;95000-99999"
        

gi[988]['text'] = "Hong Kong, China"
gi[988]['pubrange'] = "00-14;15000-16999;17000-19999;200-799;8000-9699;97000-99999"
        

gi[989]['text'] = "Portugal"
gi[989]['pubrange'] = "0-1;20-54;550-799;8000-9499;95000-99999"
        

gi[9927]['text'] = "Qatar"
gi[9927]['pubrange'] = "00-09;100-399;4000-4999"
        

gi[9928]['text'] = "Albania"
gi[9928]['pubrange'] = "00-09;100-399;4000-4999"
        

gi[9929]['text'] = "Guatemala"
gi[9929]['pubrange'] = "0-3;40-54;550-799;8000-9999"
        

gi[9930]['text'] = "Costa Rica"
gi[9930]['pubrange'] = "00-49;500-939;9400-9999"
        

gi[9931]['text'] = "Algeria"
gi[9931]['pubrange'] = "00-29;300-899;9000-9999"
        

gi[9932]['text'] = "Lao People's Democratic Republic"
gi[9932]['pubrange'] = "00-39;400-849;8500-9999"
        

gi[9933]['text'] = "Syria"
gi[9933]['pubrange'] = "0-0;10-39;400-899;9000-9999"
        

gi[9934]['text'] = "Latvia"
gi[9934]['pubrange'] = "0-0;10-49;500-799;8000-9999"
        

gi[9935]['text'] = "Iceland"
gi[9935]['pubrange'] = "0-0;10-39;400-899;9000-9999"
        

gi[9936]['text'] = "Afghanistan"
gi[9936]['pubrange'] = "0-1;20-39;400-799;8000-9999"
        

gi[9937]['text'] = "Nepal"
gi[9937]['pubrange'] = "0-2;30-49;500-799;8000-9999"
        

gi[9938]['text'] = "Tunisia"
gi[9938]['pubrange'] = "00-79;800-949;9500-9999"
        

gi[9939]['text'] = "Armenia"
gi[9939]['pubrange'] = "0-4;50-79;800-899;9000-9999"
        

gi[9940]['text'] = "Montenegro"
gi[9940]['pubrange'] = "0-1;20-49;500-899;9000-9999"
        

gi[9941]['text'] = "Georgia"
gi[9941]['pubrange'] = "0-0;10-39;400-899;9000-9999"
        

gi[9942]['text'] = "Ecuador"
gi[9942]['pubrange'] = "00-89;900-984;9850-9999"
        

gi[9943]['text'] = "Uzbekistan"
gi[9943]['pubrange'] = "00-29;300-399;4000-9999"
        

gi[9944]['text'] = "Turkey"
gi[9944]['pubrange'] = "0000-0999;100-499;5000-5999;60-69;700-799;80-89;900-999"
        

gi[9945]['text'] = "Dominican Republic"
gi[9945]['pubrange'] = "00-00;010-079;08-39;400-569;57-57;580-849;8500-9999"
        

gi[9946]['text'] = "Korea, P.D.R."
gi[9946]['pubrange'] = "0-1;20-39;400-899;9000-9999"
        

gi[9947]['text'] = "Algeria"
gi[9947]['pubrange'] = "0-1;20-79;800-999"
        

gi[9948]['text'] = "United Arab Emirates"
gi[9948]['pubrange'] = "00-39;400-849;8500-9999"
        

gi[9949]['text'] = "Estonia"
gi[9949]['pubrange'] = "0-0;10-39;400-899;9000-9999"
        

gi[9950]['text'] = "Palestine"
gi[9950]['pubrange'] = "00-29;300-849;8500-9999"
        

gi[9951]['text'] = "Kosova"
gi[9951]['pubrange'] = "00-39;400-849;8500-9999"
        

gi[9952]['text'] = "Azerbaijan"
gi[9952]['pubrange'] = "0-1;20-39;400-799;8000-9999"
        

gi[9953]['text'] = "Lebanon"
gi[9953]['pubrange'] = "0-0;10-39;400-599;60-89;9000-9999"
        

gi[9954]['text'] = "Morocco"
gi[9954]['pubrange'] = "0-1;20-39;400-799;8000-9999"
        

gi[9955]['text'] = "Lithuania"
gi[9955]['pubrange'] = "00-39;400-929;9300-9999"
        

gi[9956]['text'] = "Cameroon"
gi[9956]['pubrange'] = "0-0;10-39;400-899;9000-9999"
        

gi[9957]['text'] = "Jordan"
gi[9957]['pubrange'] = "00-39;400-699;70-84;8500-8799;88-99"
        

gi[9958]['text'] = "Bosnia and Herzegovina"
gi[9958]['pubrange'] = "00-03;040-089;0900-0999;10-18;1900-1999;20-49;500-899;9000-9999"
        

gi[9959]['text'] = "Libya"
gi[9959]['pubrange'] = "0-1;20-79;800-949;9500-9999"
        

gi[9960]['text'] = "Saudi Arabia"
gi[9960]['pubrange'] = "00-59;600-899;9000-9999"
        

gi[9961]['text'] = "Algeria"
gi[9961]['pubrange'] = "0-2;30-69;700-949;9500-9999"
        

gi[9962]['text'] = "Panama"
gi[9962]['pubrange'] = "00-54;5500-5599;56-59;600-849;8500-9999"
        

gi[9963]['text'] = "Cyprus"
gi[9963]['pubrange'] = "0-2;30-54;550-734;7350-7499;7500-9999"
        

gi[9964]['text'] = "Ghana"
gi[9964]['pubrange'] = "0-6;70-94;950-999"
        

gi[9965]['text'] = "Kazakhstan"
gi[9965]['pubrange'] = "00-39;400-899;9000-9999"
        

gi[9966]['text'] = "Kenya"
gi[9966]['pubrange'] = "000-149;1500-1999;20-69;7000-7499;750-959;9600-9999"
        

gi[9967]['text'] = "Kyrgyz Republic"
gi[9967]['pubrange'] = "00-39;400-899;9000-9999"
        

gi[9968]['text'] = "Costa Rica"
gi[9968]['pubrange'] = "00-49;500-939;9400-9999"
        

gi[9970]['text'] = "Uganda"
gi[9970]['pubrange'] = "00-39;400-899;9000-9999"
        

gi[9971]['text'] = "Singapore"
gi[9971]['pubrange'] = "0-5;60-89;900-989;9900-9999"
        

gi[9972]['text'] = "Peru"
gi[9972]['pubrange'] = "00-09;1-1;200-249;2500-2999;30-59;600-899;9000-9999"
        

gi[9973]['text'] = "Tunisia"
gi[9973]['pubrange'] = "00-05;060-089;0900-0999;10-69;700-969;9700-9999"
        

gi[9974]['text'] = "Uruguay"
gi[9974]['pubrange'] = "0-2;30-54;550-749;7500-9499;95-99"
        

gi[9975]['text'] = "Moldova"
gi[9975]['pubrange'] = "0-0;100-399;4000-4499;45-89;900-949;9500-9999"
        

gi[9976]['text'] = "Tanzania"
gi[9976]['pubrange'] = "0-5;60-89;900-989;9900-9999"
        

gi[9977]['text'] = "Costa Rica"
gi[9977]['pubrange'] = "00-89;900-989;9900-9999"
        

gi[9978]['text'] = "Ecuador"
gi[9978]['pubrange'] = "00-29;300-399;40-94;950-989;9900-9999"
        

gi[9979]['text'] = "Iceland"
gi[9979]['pubrange'] = "0-4;50-64;650-659;66-75;760-899;9000-9999"
        

gi[9980]['text'] = "Papua New Guinea"
gi[9980]['pubrange'] = "0-3;40-89;900-989;9900-9999"
        

gi[9981]['text'] = "Morocco"
gi[9981]['pubrange'] = "00-09;100-159;1600-1999;20-79;800-949;9500-9999"
        

gi[9982]['text'] = "Zambia"
gi[9982]['pubrange'] = "00-79;800-989;9900-9999"
        

gi[9983]['text'] = "Gambia"
gi[9983]['pubrange'] = "80-94;950-989;9900-9999"
        

gi[9984]['text'] = "Latvia"
gi[9984]['pubrange'] = "00-49;500-899;9000-9999"
        

gi[9985]['text'] = "Estonia"
gi[9985]['pubrange'] = "0-4;50-79;800-899;9000-9999"
        

gi[9986]['text'] = "Lithuania"
gi[9986]['pubrange'] = "00-39;400-899;9000-9399;940-969;97-99"
        

gi[9987]['text'] = "Tanzania"
gi[9987]['pubrange'] = "00-39;400-879;8800-9999"
        

gi[9988]['text'] = "Ghana"
gi[9988]['pubrange'] = "0-2;30-54;550-749;7500-9999"
        

gi[9989]['text'] = "Macedonia"
gi[9989]['pubrange'] = "0-0;100-199;2000-2999;30-59;600-949;9500-9999"
        

gi[99901]['text'] = "Bahrain"
gi[99901]['pubrange'] = "00-49;500-799;80-99"
        

gi[99902]['text'] = "Gabon"
gi[99902]['pubrange'] = ""
        

gi[99903]['text'] = "Mauritius"
gi[99903]['pubrange'] = "0-1;20-89;900-999"
        

gi[99904]['text'] = "Netherlands Antilles and Aruba"
gi[99904]['pubrange'] = "0-5;60-89;900-999"
        

gi[99905]['text'] = "Bolivia"
gi[99905]['pubrange'] = "0-3;40-79;800-999"
        

gi[99906]['text'] = "Kuwait"
gi[99906]['pubrange'] = "0-2;30-59;600-699;70-89;90-94;950-999"
        

gi[99908]['text'] = "Malawi"
gi[99908]['pubrange'] = "0-0;10-89;900-999"
        

gi[99909]['text'] = "Malta"
gi[99909]['pubrange'] = "0-3;40-94;950-999"
        

gi[99910]['text'] = "Sierra Leone"
gi[99910]['pubrange'] = "0-2;30-89;900-999"
        

gi[99911]['text'] = "Lesotho"
gi[99911]['pubrange'] = "00-59;600-999"
        

gi[99912]['text'] = "Botswana"
gi[99912]['pubrange'] = "0-3;400-599;60-89;900-999"
        

gi[99913]['text'] = "Andorra"
gi[99913]['pubrange'] = "0-2;30-35;600-604"
        

gi[99914]['text'] = "Suriname"
gi[99914]['pubrange'] = "0-4;50-89;900-999"
        

gi[99915]['text'] = "Maldives"
gi[99915]['pubrange'] = "0-4;50-79;800-999"
        

gi[99916]['text'] = "Namibia"
gi[99916]['pubrange'] = "0-2;30-69;700-999"
        

gi[99917]['text'] = "Brunei Darussalam"
gi[99917]['pubrange'] = "0-2;30-89;900-999"
        

gi[99918]['text'] = "Faroe Islands"
gi[99918]['pubrange'] = "0-3;40-79;800-999"
        

gi[99919]['text'] = "Benin"
gi[99919]['pubrange'] = "0-2;300-399;40-69;850-899;900-999"
        

gi[99920]['text'] = "Andorra"
gi[99920]['pubrange'] = "0-4;50-89;900-999"
        

gi[99921]['text'] = "Qatar"
gi[99921]['pubrange'] = "0-1;20-69;700-799;8-8;90-99"
        

gi[99922]['text'] = "Guatemala"
gi[99922]['pubrange'] = "0-3;40-69;700-999"
        

gi[99923]['text'] = "El Salvador"
gi[99923]['pubrange'] = "0-1;20-79;800-999"
        

gi[99924]['text'] = "Nicaragua"
gi[99924]['pubrange'] = "0-1;20-79;800-999"
        

gi[99925]['text'] = "Paraguay"
gi[99925]['pubrange'] = "0-3;40-79;800-999"
        

gi[99926]['text'] = "Honduras"
gi[99926]['pubrange'] = "0-0;10-59;600-899;90-99"
        

gi[99927]['text'] = "Albania"
gi[99927]['pubrange'] = "0-2;30-59;600-999"
        

gi[99928]['text'] = "Georgia"
gi[99928]['pubrange'] = "0-0;10-79;800-999"
        

gi[99929]['text'] = "Mongolia"
gi[99929]['pubrange'] = "0-4;50-79;800-999"
        

gi[99930]['text'] = "Armenia"
gi[99930]['pubrange'] = "0-4;50-79;800-999"
        

gi[99931]['text'] = "Seychelles"
gi[99931]['pubrange'] = "0-4;50-79;800-999"
        

gi[99932]['text'] = "Malta"
gi[99932]['pubrange'] = "0-0;10-59;600-699;7-7;80-99"
        

gi[99933]['text'] = "Nepal"
gi[99933]['pubrange'] = "0-2;30-59;600-999"
        

gi[99934]['text'] = "Dominican Republic"
gi[99934]['pubrange'] = "0-1;20-79;800-999"
        

gi[99935]['text'] = "Haiti"
gi[99935]['pubrange'] = "0-2;30-59;600-699;7-8;90-99"
        

gi[99936]['text'] = "Bhutan"
gi[99936]['pubrange'] = "0-0;10-59;600-999"
        

gi[99937]['text'] = "Macau"
gi[99937]['pubrange'] = "0-1;20-59;600-999"
        

gi[99938]['text'] = "Srpska, Republic of"
gi[99938]['pubrange'] = "0-1;20-59;600-899;90-99"
        

gi[99939]['text'] = "Guatemala"
gi[99939]['pubrange'] = "0-5;60-89;900-999"
        

gi[99940]['text'] = "Georgia"
gi[99940]['pubrange'] = "0-0;10-69;700-999"
        

gi[99941]['text'] = "Armenia"
gi[99941]['pubrange'] = "0-2;30-79;800-999"
        

gi[99942]['text'] = "Sudan"
gi[99942]['pubrange'] = "0-4;50-79;800-999"
        

gi[99943]['text'] = "Albania"
gi[99943]['pubrange'] = "0-2;30-59;600-999"
        

gi[99944]['text'] = "Ethiopia"
gi[99944]['pubrange'] = "0-4;50-79;800-999"
        

gi[99945]['text'] = "Namibia"
gi[99945]['pubrange'] = "0-5;60-89;900-999"
        

gi[99946]['text'] = "Nepal"
gi[99946]['pubrange'] = "0-2;30-59;600-999"
        

gi[99947]['text'] = "Tajikistan"
gi[99947]['pubrange'] = "0-2;30-69;700-999"
        

gi[99948]['text'] = "Eritrea"
gi[99948]['pubrange'] = "0-4;50-79;800-999"
        

gi[99949]['text'] = "Mauritius"
gi[99949]['pubrange'] = "0-1;20-89;900-999"
        

gi[99950]['text'] = "Cambodia"
gi[99950]['pubrange'] = "0-4;50-79;800-999"
        

gi[99951]['text'] = "Congo, The Democratic Republic"
gi[99951]['pubrange'] = ""
        

gi[99952]['text'] = "Mali"
gi[99952]['pubrange'] = "0-4;50-79;800-999"
        

gi[99953]['text'] = "Paraguay"
gi[99953]['pubrange'] = "0-2;30-79;800-939;94-99"
        

gi[99954]['text'] = "Bolivia"
gi[99954]['pubrange'] = "0-2;30-69;700-999"
        

gi[99955]['text'] = "Srpska, Republic of"
gi[99955]['pubrange'] = "0-1;20-59;600-799;80-89;90-99"
        

gi[99956]['text'] = "Albania"
gi[99956]['pubrange'] = "00-59;600-859;86-99"
        

gi[99957]['text'] = "Malta"
gi[99957]['pubrange'] = "0-1;20-79;800-999"
        

gi[99958]['text'] = "Bahrain"
gi[99958]['pubrange'] = "0-4;50-94;950-999"
        

gi[99959]['text'] = "Luxembourg"
gi[99959]['pubrange'] = "0-2;30-59;600-999"
        

gi[99960]['text'] = "Malawi"
gi[99960]['pubrange'] = "0-0;10-94;950-999"
        

gi[99961]['text'] = "El Salvador"
gi[99961]['pubrange'] = "0-3;40-89;900-999"
        

gi[99962]['text'] = "Mongolia"
gi[99962]['pubrange'] = "0-4;50-79;800-999"
        

gi[99963]['text'] = "Cambodia"
gi[99963]['pubrange'] = "00-49;500-999"
        

gi[99964]['text'] = "Nicaragua"
gi[99964]['pubrange'] = "0-1;20-79;800-999"
        

gi[99965]['text'] = "Macau"
gi[99965]['pubrange'] = "0-3;40-79;800-999"
        

gi[99966]['text'] = "Kuwait"
gi[99966]['pubrange'] = "0-2;30-69;700-799"
        

gi[99967]['text'] = "Paraguay"
gi[99967]['pubrange'] = "0-1;20-59;600-899"
        

gi[99968]['text'] = "Botswana"
gi[99968]['pubrange'] = "0-3;400-599;60-89;900-999"
        

gi[99969]['text'] = "Oman"
gi[99969]['pubrange'] = "0-4;50-79;800-999"


def get_country_index(gtin):
    """
    >>> get_country_index('9789996900006')
    99969
    >>> get_country_index('9789997000002')
    -1
    """
    assert int(gtin.replace("-",""))
    for icountry in countries:
        if gtin[3:].find(str(icountry)) == 0:
            return icountry
    return -1


def prefix_array(su, sl):
    pl = len(su)
    assert pl == len(sl)
    return [str(i).zfill(pl) for i in range(int(su), int(sl) + 1)]

# def split_isbn(self,i1,i2): # FIXME - coverage
#     part0 = self.arg[0:3]
#     part1 = self.arg[3:3+i1]
#     part2 = self.arg[3+i1:3+i2]
#     part3 = self.arg[3+i2:-1]
#     part4 = self.arg[-1]
#     assert self.arg == "%s%s%s%s%s" % (part0,part1,part2,part3,part4)
#     return "ISBN %s-%s-%s-%s-%s" % (part0,part1,part2,part3,part4)


def get_publisher_id(sub_gtin, prefixes):
    #print locals()
    for prefix in prefixes:
        if sub_gtin.find(prefix) == 0:
            return prefix
    return False


def hyphenate(gtin):
    """
    >>> hyphenate('9780140150988')
    ('978-0-14-015098-8', 'English language')

    >>> hyphenate('9789995710101')
    ('978-99957-1-010-1', 'Malta')

    >>> hyphenate('9789996700002')
    ('978-99967-0-000-2', 'Paraguay')

    >>> hyphenate('9789996790003')
    (False, False)

    """
    ret = [gtin[0:3]]
    country_index = get_country_index(gtin)
    if country_index == -1:
        return False
    country = gi.get(country_index)
    #print '-----------'
    #print gtin, country_index, country
    if country_index > -1:
        ret.append(str(country_index))
    else:
        return False, False
    #print ret
    pubrange = country['pubrange'].split(";")
    #print pubrange
    for k in pubrange:
        su, sl = k.split('-')
        pub_id = get_publisher_id(gtin[3+len(str(country_index)):], prefix_array(su, sl))
        if pub_id:
            ret.append(pub_id)
            ret.append(gtin[3+len(str(country_index))+len(pub_id):-1])  # book
            ret.append(gtin[-1])  # cd
            assert gtin == ''.join(ret)
            return '-'.join(ret), country['text']
    return False, False

# if __name__ == '__main__':
#     assert hyphenate('9780140150988') == ('978-0-14-015098-8', 'English language')
#     assert hyphenate('9789995710101') == ('978-99957-1-010-1', 'Malta')
#     assert hyphenate('9789996700002') == ('978-99967-0-000-2', 'Paraguay')
#     assert hyphenate('9789996790003') == (False,False)
