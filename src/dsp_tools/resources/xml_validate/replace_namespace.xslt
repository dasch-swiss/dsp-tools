<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0"
                xmlns:knora="https://dasch.swiss/schema"
                exclude-result-prefixes="knora">

  <!-- Define the parameter to receive the replacement value from Python -->
  <xsl:param name="replacementValue"/>

  <xsl:template match="*">
    <xsl:copy>
      <!-- Process the attributes -->
      <xsl:for-each select="@*">
        <xsl:choose>
          <!-- For restype: Leave unchanged if it starts with knora-api or replacementValue -->
          <xsl:when test="name() = 'restype' and (starts-with(., 'http://') or starts-with(., concat('-', $replacementValue)))">
            <xsl:attribute name="restype">
              <xsl:value-of select="." />
            </xsl:attribute>
          </xsl:when>
          <!-- For restype: Replace the colon with the custom value if not knora-api or replacementValue -->
          <xsl:when test="name() = 'restype' and contains(., ':')">
            <xsl:attribute name="restype">
              <xsl:value-of select="concat(substring-before(., ':'), $replacementValue, substring-after(., ':'))" />
            </xsl:attribute>
          </xsl:when>
          <!-- For restype: Prepend knora-api if no colon is found and no special prefixes -->
          <xsl:when test="name() = 'restype' and not(contains(., ':'))">
            <xsl:attribute name="restype">
              <xsl:value-of select="concat('http://api.knora.org/ontology/knora-api/v2#', .)" />
            </xsl:attribute>
          </xsl:when>
          <!-- For name: Leave unchanged if it starts with knora-api or replacementValue -->
          <xsl:when test="name() = 'name' and (starts-with(., 'http://') or starts-with(., concat('-', $replacementValue)))">
            <xsl:attribute name="name">
              <xsl:value-of select="." />
            </xsl:attribute>
          </xsl:when>
          <!-- For restype: Replace the colon with the custom value if not knora-api or replacementValue -->
          <xsl:when test="name() = 'name' and contains(., ':')">
            <xsl:attribute name="name">
              <xsl:value-of select="concat(substring-before(., ':'), $replacementValue, substring-after(., ':'))" />
            </xsl:attribute>
          </xsl:when>
          <!-- For restype: Prepend knora-api if no colon is found and no special prefixes -->
          <xsl:when test="name() = 'name' and not(contains(., ':'))">
            <xsl:attribute name="name">
              <xsl:value-of select="concat('http://api.knora.org/ontology/knora-api/v2#', .)" />
            </xsl:attribute>
          </xsl:when>
          <!-- Copy other attributes unchanged -->
          <xsl:otherwise>
            <xsl:copy-of select="."/>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>

      <!-- Process child elements -->
      <xsl:apply-templates/>
    </xsl:copy>
  </xsl:template>

</xsl:stylesheet>
