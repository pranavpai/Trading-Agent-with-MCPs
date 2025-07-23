from agents import TracingProcessor, Trace, Span
from database import write_log
import secrets
import string
import json
import time

ALPHANUM = string.ascii_lowercase + string.digits 

def make_trace_id(tag: str) -> str:
    """
    Return a string of the form 'trace_<tag><random>',
    where the total length after 'trace_' is 32 chars.
    """
    tag += "0"
    pad_len = 32 - len(tag)
    random_suffix = ''.join(secrets.choice(ALPHANUM) for _ in range(pad_len))
    return f"trace_{tag}{random_suffix}"

class LogTracer(TracingProcessor):
    def __init__(self):
        self.tool_start_times = {}

    def get_name(self, trace_or_span: Trace | Span) -> str | None:
        trace_id = trace_or_span.trace_id
        name = trace_id.split("_")[1]
        if '0' in name:
            return name.split("0")[0]
        else:
            return None

    def on_trace_start(self, trace) -> None:
        name = self.get_name(trace)
        if name:
            write_log(name, "trace", f"Started: {trace.name}")

    def on_trace_end(self, trace) -> None:
        name = self.get_name(trace)
        if name:
            write_log(name, "trace", f"Ended: {trace.name}")

    def on_span_start(self, span) -> None:
        name = self.get_name(span)
        type = span.span_data.type if span.span_data else "span"
        if name:
            # Track tool call start time for duration calculation
            span_key = f"{span.trace_id}_{span.span_id}"
            self.tool_start_times[span_key] = time.time()
            
            # Check if this is an MCP tool call
            if span.span_data and span.span_data.type == "function":
                tool_name = getattr(span.span_data, "name", "unknown_tool")
                # Log MCP tool call start
                message = f"🔧 {tool_name}"
                if hasattr(span.span_data, "server") and span.span_data.server:
                    message += f" [{span.span_data.server}]"
                write_log(name, "mcp_tool", f"{message} - Starting...")
                return
            
            # Regular span logging for non-tool calls
            message = "Started"
            if span.span_data:
                if span.span_data.type:
                    message += f" {span.span_data.type}"
                if hasattr(span.span_data, "name") and span.span_data.name:
                    message += f" {span.span_data.name}"
                if hasattr(span.span_data, "server") and span.span_data.server:
                    message += f" {span.span_data.server}"
            if span.error:
                message += f" {span.error}"
            write_log(name, type, message)

    def on_span_end(self, span) -> None:
        name = self.get_name(span)
        type = span.span_data.type if span.span_data else "span"
        if name:
            # Calculate execution duration
            span_key = f"{span.trace_id}_{span.span_id}"
            duration = 0
            if span_key in self.tool_start_times:
                duration = time.time() - self.tool_start_times[span_key]
                del self.tool_start_times[span_key]
            
            # Check if this is an MCP tool call
            if span.span_data and span.span_data.type == "function":
                tool_name = getattr(span.span_data, "name", "unknown_tool")
                status = "✅" if not span.error else "❌"
                
                # Format tool result message
                result_summary = ""
                if hasattr(span.span_data, "result") and span.span_data.result:
                    try:
                        result = span.span_data.result
                        if isinstance(result, str) and len(result) > 100:
                            result_summary = f" → {result[:97]}..."
                        else:
                            result_summary = f" → {result}"
                    except:
                        result_summary = " → [result]"
                
                message = f"🔧 {tool_name}{result_summary} [{duration:.1f}s] {status}"
                if span.error:
                    message += f" Error: {span.error}"
                    
                write_log(name, "mcp_tool", message)
                return
            
            # Regular span logging for non-tool calls
            message = "Ended"
            if span.span_data:
                if span.span_data.type:
                    message += f" {span.span_data.type}"
                if hasattr(span.span_data, "name") and span.span_data.name:
                    message += f" {span.span_data.name}"
                if hasattr(span.span_data, "server") and span.span_data.server:
                    message += f" {span.span_data.server}"
            if span.error:
                message += f" {span.error}"
            write_log(name, type, message)

    def force_flush(self) -> None:
        pass

    def shutdown(self) -> None:
        pass