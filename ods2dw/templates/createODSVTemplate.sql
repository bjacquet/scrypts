/**
Description:
	Generated file.

	Creates a View for table [ods].[ODST%(tablename)s].
Author:
	Bruno Jacquet 05.2009
*/
create view [ods].[ODSV%(tablename)s]
AS
SELECT
%(columns)s
t2.[Dbatchdate]
from [ods].[ODST%(tablename)s] t1
     cross join [dw].[DWT000_SP] t2
