/**
Description:
	Splits a given string into words.
Arguments:
	@Keyword varchar(8000) - the string to be splited
	@Delimiter varchar(255) - delimiter to split the string into words
Return Value:
	@SplitKeyword - splited words table
Author & Date:
	Bruno Jacquet 02.2009
*/
if OBJECT_ID('dbo.f_Split', 'FN') is not null
	drop function dbo.f_Split
go

CREATE FUNCTION dbo.f_Split
(
 @Keyword VARCHAR(8000),
 @Delimiter VARCHAR(255)
)
RETURNS @SplitKeyword TABLE (Keyword VARCHAR(8000))
AS
BEGIN
 DECLARE @Word VARCHAR(255)
 DECLARE @TempKeyword TABLE (Keyword VARCHAR(8000))

 WHILE (CHARINDEX(@Delimiter, @Keyword, 1)>0)
 BEGIN
  SET @Word = SUBSTRING(@Keyword, 1 , CHARINDEX(@Delimiter, @Keyword, 1) - 1)
  SET @Keyword = SUBSTRING(@Keyword, CHARINDEX(@Delimiter, @Keyword, 1) + 1, LEN(@Keyword))
  INSERT INTO @TempKeyword VALUES(@Word)
 END
 
 INSERT INTO @TempKeyword VALUES(@Keyword)
 
 INSERT @SplitKeyword
 SELECT * FROM @TempKeyword
 RETURN
END
