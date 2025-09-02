package org.licenselynx;

/**
 * Handler for quotes in input strings.
 */
final class QuotesHandler
{

    // Array of quote characters to be replaced.
    private static final char[] QUOTE_CHARACTERS = {
            // Single quotes
            '‘', // LEFT SINGLE QUOTATION MARK
            '’', // RIGHT SINGLE QUOTATION MARK
            '‚', // SINGLE LOW-9 QUOTATION MARK
            '‛', // SINGLE HIGH-REVERSED-9 QUOTATION MARK
            '′', // PRIME (often used as an apostrophe)
            '＇', // FULLWIDTH APOSTROPHE
            // Double quotes
            '“', // LEFT DOUBLE QUOTATION MARK
            '”', // RIGHT DOUBLE QUOTATION MARK
            '„', // DOUBLE LOW-9 QUOTATION MARK
            '‟', // DOUBLE HIGH-REVERSED-9 QUOTATION MARK
            '″', // DOUBLE PRIME
            '«', // LEFT-POINTING DOUBLE ANGLE QUOTATION MARK
            '»', // RIGHT-POINTING DOUBLE ANGLE QUOTATION MARK
            '＂'  // FULLWIDTH QUOTATION MARK
    };

    // Private constructor prevents instantiation.
    private QuotesHandler()
    {
        throw new AssertionError("Utility class should not be instantiated.");
    }

    /**
     * Normalizes the input string by replacing various Unicode quote characters
     * with the default replacement (') character.
     *
     * @param pInputString The input text that may contain various quote characters.
     * @return The normalized text with all recognized quote characters replaced.
     */
    public static String normalizeQuotes(final String pInputString)
    {
        return normalizeQuotes(pInputString, "'");
    }

    /**
     * Normalizes the input string by replacing various Unicode quote characters
     * with a specified replacement string.
     *
     * @param pInputString The input text that may contain various quote characters.
     * @param pReplacement The quote character replacement to use.
     * @return The normalized text with all recognized quote characters replaced.
     */
    public static String normalizeQuotes(final String pInputString, final String pReplacement)
    {
        if (pInputString == null)
        {
            return null;
        }

        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < pInputString.length(); i++)
        {
            char c = pInputString.charAt(i);
            if (isQuoteCharacter(c))
            {
                sb.append(pReplacement);
            }
            else {
                sb.append(c);
            }
        }
        return sb.toString();
    }

    /**
     * Checks whether the given character is in the defined list of quote characters.
     *
     * @param pCharacter The character to check.
     * @return True if the character is a quote character, false otherwise.
     */
    private static boolean isQuoteCharacter(final char pCharacter)
    {
        for (char quote : QUOTE_CHARACTERS)
        {
            if (quote == pCharacter)
            {
                return true;
            }
        }
        return false;
    }
}
