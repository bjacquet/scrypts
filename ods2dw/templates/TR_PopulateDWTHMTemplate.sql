
if dbo.f_Trigger_id('DWT%(table_number)s_Populate_DWT%(table_number)sHM') is not null
    drop trigger dw.DWT%(table_number)s_Populate_DWT%(table_number)sHM
go
CREATE TRIGGER dw.DWT%(table_number)s_Populate_DWT%(table_number)sHM
    ON  dw.DWT%(table_name)s
    AFTER INSERT
AS 

/**
Description:
    Generated file.

    Trigger for every INSERT query on table "dw.DWT%(table_name)s".

    If the value of "dw.DWT000_SP.Fendoofmonth" is 'True' then it 
    copies table "dw.DWT%(table_name)s" to "dw.DWT%(historic_table_name)s" with 
    the 'YYYYMM' of "dw.DWT000_SP.Dbatchdate" on 
    "dw.DWT%(historic_table_name)s.Dbatchdate".
Author & Date:
    Bruno Jacquet 05.2009
*/

BEGIN
    SET NOCOUNT ON;

    if (select Fendofmonth from dw.DWT000_SP) is not NULL AND (select Fendofmonth from dw.DWT000_SP) = 1 begin
        print 'Populating DWT%(historic_table_name)s'

	INSERT INTO [DataWarehouse].[dw].[DWT%(historic_table_name)s]
	    (%(dw_columns)s)
	SELECT
	    %(dwh_columns)s
	FROM [DataWarehouse].[dw].[DWT%(table_name)s]

    end

END
