-- First shipment using the location as origin site ----

IF OBJECT_ID(N'tempdb..#origin_shipment') IS NOT NULL DROP TABLE #origin_shipment 
SELECT [from_location_id]
     ,create_datetime AS 'origin_site_shipment_create'
     ,shipment_id
    -- ,shipment_status
INTO #origin_shipment
FROM (
    SELECT [shipment_id]
    --,S.status AS 'shipment_status'
      ,L.customer_id
      ,[from_location_id]
      --,[to_location_id]
      ,[create_datetime]
     -- ,[ready_datetime]
      --,[shipped_datetime]
      --,[closed_datetime]
      ,shipment_number = ROW_NUMBER() OVER (PARTITION BY S.from_location_id ORDER BY create_datetime ASC)
  FROM [dwh].[Location] L
  LEFT JOIN [dwh].[acm_shipments] S on S.from_location_id = L.location_id
  WHERE L.customer_id = 123
  AND L.status = 2 -- active locations
   AND S.status In (2,3,4-) -- shipping, dleivered, closed,  shipments
) O
WHERE shipment_number = 1

-- First shipment using the location as destination site ----

IF OBJECT_ID(N'tempdb..#destination_shipment') IS NOT NULL DROP TABLE #destination_shipment 
SELECT [to_location_id]
     ,create_datetime AS 'destination_site_shipment_create'
     ,shipment_id
    -- ,shipment_status 
INTO #destination_shipment
FROM (
    SELECT [shipment_id]
   -- ,S.status AS 'shipment_status'
      ,L.customer_id
      ,[to_location_id]
      --,[to_location_id]
      ,[create_datetime]
     -- ,[ready_datetime]
      --,[shipped_datetime]
      --,[closed_datetime]
      ,shipment_number = ROW_NUMBER() OVER (PARTITION BY S.to_location_id ORDER BY create_datetime ASC)
  FROM [dwh].[Location] L
  LEFT JOIN [dwh].[acm_shipments] S on S.to_location_id = L.location_id
  WHERE L.customer_id = 12
  AND L.status = 2 -- active locations
   AND S.status In (2,3,4-) -- shipping, dleivered, closed,  shipments
) O
WHERE shipment_number = 1


-- Summary 

SELECT  [location_id]
      ,[ref_id]
     --,[status]
      ,[name]
      ,[address_1]
      --,[address_2]
      ,[city]
      ,[postcode]
      ,[country]
      ,[create_ts]
      ,DATEADD(SECOND, create_ts, '1970-01-01') AS 'location_created'
        ,origin_site_shipment_create
        ,O.shipment_id
       -- ,O.shipment_status
        ,DATEPART(YEAR,origin_site_shipment_create) AS 'origin_year'
        ,destination_site_shipment_create
        ,D.shipment_id
       -- ,D.shipment_status
        ,DATEPART(YEAR,destination_site_shipment_create) AS 'destination_year'
      --,[address_3]
  FROM [dwh].[Location] L 
  LEFT JOIN #origin_shipment O on O.from_location_id = L.location_id
  LEFT JOIN #destination_shipment D on D.to_location_id = L.location_id
  WHERE customer_id = 123
  AND status = 2 -- active locations
