create view [dw].[DWV%(tablename)s]
AS
SELECT
	%(columns)s
	t1.[Dbatchdate]
from [dw].[DWT%(tablename)s] t1
	inner join [dw].[DWT000_SP] t2	
	      on t1.Dbatchdate = t2.Dbatchdate
