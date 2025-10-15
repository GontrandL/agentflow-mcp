#!/bin/bash
# MCP Server Performance Monitor
# Usage: ./monitor_mcp.sh

cd "$(dirname "$0")"

echo "================================================================================"
echo "🔍 MCP SERVER PERFORMANCE MONITOR"
echo "================================================================================"
echo ""

echo "📊 Tool Call Summary (Last Hour):"
find logs/mcp -name "*.log" -mmin -60 -exec grep "tool_called" {} \; 2>/dev/null | \
  grep -oP 'tool": "\K[^"]+' | sort | uniq -c | sort -rn || echo "No data yet"

echo ""
echo "⚡ Average Compression Ratio:"
find logs/mcp -name "*.log" -mmin -60 -exec grep "compression_ratio" {} \; 2>/dev/null | \
  grep -oP 'compression_ratio": \K[0-9.]+' | \
  awk '{sum+=$1; count++} END {if(count>0) print sum/count "x"; else print "No data yet"}'

echo ""
echo "✅ Average Validation Score:"
find logs/mcp -name "*.log" -mmin -60 -exec grep "validation_score" {} \; 2>/dev/null | \
  grep -oP 'validation_score": \K[0-9]+' | \
  awk '{sum+=$1; count++} END {if(count>0) print sum/count "/100"; else print "No data yet"}'

echo ""
echo "❌ Error Count (Last Hour):"
find logs/mcp -name "*.log" -mmin -60 -exec grep -c "ERROR" {} \; 2>/dev/null | \
  awk '{sum+=$1} END {print sum}'

echo ""
echo "⚠️  Warning Count (Last Hour):"
find logs/mcp -name "*.log" -mmin -60 -exec grep -c "WARNING" {} \; 2>/dev/null | \
  awk '{sum+=$1} END {print sum}'

echo ""
echo "🕒 Last 5 Tool Calls:"
if [ -f logs/mcp/apc_mcp_server.log ]; then
  tail -5 logs/mcp/apc_mcp_server.log | grep "tool_called" || echo "No tool calls yet"
else
  echo "Log file not created yet - waiting for first MCP call"
fi

echo ""
echo "📈 MCP Server Status:"
if [ -f logs/mcp/apc_mcp_server.log ]; then
  echo "✅ APC MCP Server: Active (log exists)"
else
  echo "🔄 APC MCP Server: Not yet deployed"
fi

echo ""
echo "================================================================================"
echo "Run 'tail -f logs/mcp/*.log' to monitor in real-time"
echo "================================================================================"
