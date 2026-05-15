from mcp.server.fastmcp import FastMCP
from app.rag import rag_retriever
from app.tools.damage_estimator import damage_estimator
from app.tools.claim_status import get_claim_status
from app.tools.policy_compare import compare_policies
from app.schemas import Source

# Create MCP server
mcp = FastMCP("HomeShield Insurance Copilot", host="127.0.0.1", port=5000)

@mcp.tool()
def search_policy(query: str, policy_type: str = None) -> str:
    """Search HomeShield policy documents and return relevant text chunks with citations."""
    results = rag_retriever.search(query, policy_type=policy_type)
    if not results:
        return "No relevant policy information found."
    output = []
    for r in results[:3]:
        output.append(f"Source: {r['document']} (score {r['score']:.2f})\n{r['text'][:500]}...")
    return "\n\n".join(output)

@mcp.tool()
def estimate_repair_cost(damage_type: str, property_size_category: str = None, peril_category: str = None) -> str:
    """Get indicative repair cost range for a given damage type and property size."""
    result = damage_estimator.estimate(
        damage_type=damage_type,
        property_size_category=property_size_category,
        peril_category=peril_category,
    )
    if not result["found"]:
        return result["message"]
    matches = result["matches"][:2]
    lines = []
    for m in matches:
        lines.append(f"- {m['damage_type']} | {m['property_size_category']}: £{m['repair_cost_low_gbp']} – £{m['repair_cost_high_gbp']} (avg £{m['repair_cost_avg_gbp']})")
    lines.append("\n*This is an indicative estimate only, not a claim approval.*")
    return "\n".join(lines)

@mcp.tool()
def get_claim_status(claim_id: str) -> str:
    """Simulated claim status lookup by claim ID."""
    status = get_claim_status(claim_id)
    return f"Claim {status.claim_id}: {status.status}. Next step: {status.next_step}"

@mcp.tool()
def compare_policy_tiers() -> str:
    """Compare coverage limits and features of Standard, Comprehensive, and Landlord Plus policies."""
    summary = compare_policies()
    output = "Policy Comparison:\n"
    for tier, details in summary.items():
        output += f"\n**{tier}**\n"
        for k, v in list(details.items())[:5]:  # limit length
            output += f"- {k.replace('_', ' ').title()}: {v}\n"
    return output

if __name__ == "__main__":
    mcp.run()