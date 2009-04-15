CREATE FUNCTION f_Split
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
