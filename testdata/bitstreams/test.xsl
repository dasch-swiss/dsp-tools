<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="https://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
  <html>
  <body>
    <h2>Title</h2>
    <xsl:for-each select="Example">
    <a>
    <xsl:attribute name="href">
    <xsl:value-of select="Something"/>
    </xsl:attribute>
    <xsl:value-of select="anotherthing"/>
    </a><p/>
    </xsl:for-each>
  </body>
  </html>
</xsl:template>
</xsl:stylesheet>
