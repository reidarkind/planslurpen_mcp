# Planslurpen MCP Server - Usage Examples

This document provides practical examples of how to use the Planslurpen MCP server with Claude.

## Basic Examples

### Example 1: Get Plan Interpretation

**Query:**
```
Get the plan interpretation for kommune 1106, plan RL791
```

**What Claude will do:**
- Use `planslurpen_get_plan` tool
- Parameters: kommunenummer="1106", plan_id="RL791"
- Returns: Complete AI interpretation of the plan

---

### Example 2: Look Up Property

**Query:**
```
What regulation plans apply to property 1106-45-123?
```

**What Claude will do:**
- Use `planslurpen_lookup_property` tool
- Parameters: kommunenummer="1106", gardsnummer="45", bruksnummer="123"
- Returns: List of all plans that apply to this property

---

### Example 3: Explore Available Data

**Query:**
```
What fields are available for plan RL791 in kommune 1106?
```

**What Claude will do:**
- Use `planslurpen_get_plan_fields` tool
- Parameters: kommunenummer="1106", plan_id="RL791"
- Returns: List of all available fields and classifications

---

### Example 4: Get Specific Field Data

**Query:**
```
Get the building height (byggehøyde) requirements for plan 1106/RL791
```

**What Claude will do:**
1. Use `planslurpen_get_plan_fields` to verify "byggehøyde" is available
2. Use `planslurpen_get_plan_output_json` with felt_kode="byggehøyde"
3. Returns: Only the building height data, filtered

---

## Advanced Examples

### Example 5: Compare Versions

**Query:**
```
Compare version 2 and version 3 of plan RL791 in kommune 1106
```

**What Claude will do:**
- Call `planslurpen_get_plan` twice with different version parameters
- Compare the results
- Highlight key differences

---

### Example 6: Get Markdown Summary

**Query:**
```
Give me a readable summary of plan RL791 in Haugesund
```

**What Claude will do:**
- Use `planslurpen_get_plan` with response_format="markdown"
- Returns: Human-readable Markdown format instead of JSON

---

### Example 7: Multi-Step Property Research

**Query:**
```
I'm looking at property 1106-45-123. What are the building restrictions?
```

**What Claude will do:**
1. Use `planslurpen_lookup_property` to find applicable plans
2. For each plan found, use `planslurpen_get_plan` to get details
3. Extract and summarize building restrictions from the plans
4. Present a comprehensive answer

---

### Example 8: Download Plan Documents

**Query:**
```
Get the original plan provisions document for plan 1106/RL791
```

**What Claude will do:**
- Use `planslurpen_get_plan_provisions` tool
- Returns: The original planbestemmelser (legal text)

---

## Real-World Scenarios

### Scenario 1: Developer Research

**User Context:** Property developer evaluating a site

**Query:**
```
I'm considering buying property 1106-78-456 in Haugesund for residential 
development. What are the key restrictions I should know about?
```

**Claude's Workflow:**
1. Look up property plans
2. Get detailed plan interpretations
3. Extract relevant fields (building height, utilization degree, etc.)
4. Summarize key restrictions and opportunities

---

### Scenario 2: Architect Planning

**User Context:** Architect designing a new building

**Query:**
```
For plan RL791 in Haugesund, what are the maximum building heights and 
utilization degrees for residential areas?
```

**Claude's Workflow:**
1. Get plan fields to verify data availability
2. Fetch filtered data for building height and utilization degree
3. Filter for residential classifications
4. Present results in organized format

---

### Scenario 3: Municipal Planner

**User Context:** Municipal employee answering citizen questions

**Query:**
```
A citizen at property 1106-23-789 wants to build an addition. 
Which regulation plan applies and what's allowed?
```

**Claude's Workflow:**
1. Look up applicable plans for the property
2. Get plan interpretation with focus on building regulations
3. Extract relevant provisions
4. Provide citizen-friendly explanation

---

## Tips for Best Results

### 1. Start Broad, Then Narrow

✅ **Good:**
```
1. "What plans apply to property 1106-45-123?"
2. "What are the building restrictions in plan RL791?"
3. "Get the detailed byggehøyde data for that plan"
```

❌ **Less Effective:**
```
"Get all detailed building data for all plans in Haugesund"
(Too broad, will hit character limits)
```

### 2. Use Filters for Large Plans

✅ **Good:**
```
"First, show me what fields are available for plan RL791, 
then get the utnyttingsgrad data"
```

❌ **Less Effective:**
```
"Get all data for plan RL791"
(May be truncated if plan is large)
```

### 3. Specify Format When Needed

✅ **Good:**
```
"Give me a markdown summary of plan RL791"
(Specifies format)
```

✅ **Also Good:**
```
"Get the JSON data for plan RL791"
(Explicitly requests JSON)
```

### 4. Reference Version When Needed

✅ **Good:**
```
"Get version 3 of plan RL791"
(Specifies exact version)
```

**Default:**
```
"Get plan RL791"
(Gets latest version)
```

---

## Understanding Responses

### JSON Response
- Structured data
- Good for further processing
- Contains all available fields
- May be large for complex plans

### Markdown Response
- Human-readable format
- Good for summaries
- Automatically truncated for readability
- Highlights key information

---

## Common Questions

### Q: How do I find a plan ID?

**A:** Visit https://planslurpen.no/ and search by kommune or address. The plan ID is shown in the URL (e.g., `/1106/RL791/3`).

### Q: What if I don't know the kommune number?

**A:** Kommune numbers are 4-digit codes. Common ones:
- Oslo: 0301
- Bergen: 4601
- Haugesund: 1106
- Trondheim: 5001
- Stavanger: 1103

Search online for "kommune nummer [city name]" to find others.

### Q: How do I interpret the response?

**A:** Claude will help interpret the technical planning terms. Ask follow-up questions like:
- "What does this mean in practical terms?"
- "Explain utnyttingsgrad in simple terms"
- "What building height does this allow?"

### Q: Can I compare multiple plans?

**A:** Yes! Ask Claude to compare them:
```
"Compare plan RL791 and plan RL820 in kommune 1106"
```

---

## Troubleshooting

### Response is Truncated

**Problem:** Message says "[Content truncated at 25,000 characters]"

**Solution:** Use filters:
```
1. Get available fields first
2. Request specific fields only
```

### Plan Not Found

**Problem:** Error "Plan not found"

**Solutions:**
- Verify kommune number (4 digits)
- Check plan ID spelling
- Try without version parameter
- Visit https://planslurpen.no/ to verify plan exists

### Unknown Field Name

**Problem:** Not sure what field names to use

**Solution:**
```
"What fields are available for this plan?"
```

---

## Integration Examples

### With Other Tools

Claude can combine Planslurpen data with other tools:

```
"Look up plan RL791 and create a summary document in Google Docs"
```

```
"Check the regulation plan for this property and add the restrictions 
to my Notion notes"
```

```
"Get the building restrictions and send them in a Slack message"
```

---

## Beta Service Notice

Remember that Planslurpen is in beta. If you notice any issues with the AI interpretation:

1. Visit https://planslurpen.no/
2. Locate the plan
3. Use their feedback mechanism to report issues

This helps improve the service for everyone!

---

## Additional Resources

- **Planslurpen Website:** https://planslurpen.no/
- **API Documentation:** https://planslurpen.no/api/swagger/index.html
- **MCP Documentation:** https://modelcontextprotocol.io/