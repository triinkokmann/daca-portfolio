-- Millised kanalid, asukohad ja makseviisid on?    
SELECT channel, store_location, payment_method    
FROM sales    
LIMIT 10;

-- Unikaalsed müügikanalid    
SELECT DISTINCT channel 
FROM sales;  

-- Unikaalsed kaupluste asukohad    
SELECT DISTINCT store_location 
FROM sales; 

-- Unikaalsed makseviisid    
SELECT DISTINCT payment_method 
FROM sales;

-- Online-müügid   
SELECT *
FROM sales    
WHERE channel = 'online'    
ORDER BY total_price DESC    
LIMIT 15;

-- Tehingud ilma kaupluse asukohata    
SELECT COUNT(*) AS puuduv_asukoht    
FROM sales    
WHERE store_location IS NULL;