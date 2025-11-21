"""
AI-powered log analysis using Ollama (local) or Gemini LLM.
"""

import os
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class LogAnalyzer:
    """AI-powered log analysis using Ollama (primary) or Gemini LLM (fallback)."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.ollama_model = os.getenv('OLLAMA_MODEL', 'llama3.2')
        self.gemini_api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        self.llm_mode = "mock"  # Default to mock
        self.model = None
        
        # Try Ollama first (priority 1)
        if self._check_ollama():
            self.llm_mode = "ollama"
            logger.info(f"Using Ollama at {self.ollama_url} with model {self.ollama_model}")
        # Try Gemini as fallback (priority 2)
        elif self.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.gemini_api_key)
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                self.llm_mode = "gemini"
                logger.info("Using Gemini API for log analysis")
            except ImportError:
                logger.warning("google-generativeai not available. Falling back to mock mode.")
            except Exception as e:
                logger.error(f"Error initializing Gemini: {e}. Falling back to mock mode.")
        else:
            logger.warning("No LLM available (Ollama or Gemini). Running in mock mode.")
    
    def _check_ollama(self) -> bool:
        """Check if Ollama is available and running."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if response.status_code == 200:
                tags = response.json()
                models = [m.get('name', '') for m in tags.get('models', [])]
                # Check if our preferred model exists
                if any(self.ollama_model in model for model in models):
                    return True
                # If preferred model not found, use first available
                elif models:
                    self.ollama_model = models[0].split(':')[0]
                    logger.info(f"Preferred model not found, using {self.ollama_model}")
                    return True
            return False
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")
            return False
    
    def _query_ollama(self, prompt: str) -> str:
        """Query Ollama API."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 2000
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '')
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error querying Ollama: {e}")
            return None
    
    def analyze_logs(self, logs: List[str], analysis_type: str = "summary") -> Dict[str, Any]:
        """
        Analyze logs using Ollama (primary), Gemini (fallback), or mock mode.
        
        Args:
            logs: List of log lines to analyze
            analysis_type: Type of analysis - 'summary', 'errors', 'security', 'performance'
        """
        try:
            if self.llm_mode == "mock":
                return self._mock_analyze_logs(logs, analysis_type)
            
            # Prepare logs for analysis
            log_text = '\n'.join(logs[-100:])  # Limit to last 100 lines
            
            # Create analysis prompt based on type
            prompts = {
                "summary": f"""
                Analyze the following system logs and provide a comprehensive summary:
                
                {log_text}
                
                Please provide:
                1. Overall system health assessment
                2. Key events and activities
                3. Any notable patterns or trends
                4. Recommendations for system administrators
                
                Format your response as structured text with clear sections.
                """,
                
                "errors": f"""
                Analyze the following system logs for errors, warnings, and potential issues:
                
                {log_text}
                
                Please identify:
                1. Critical errors and their severity
                2. Warning messages that need attention
                3. Failed operations or services
                4. Suggested troubleshooting steps
                5. Priority level for each issue (High/Medium/Low)
                
                Format your response with clear categorization.
                """,
                
                "security": f"""
                Analyze the following system logs for security-related events:
                
                {log_text}
                
                Please identify:
                1. Authentication attempts (successful/failed)
                2. Unauthorized access attempts
                3. Privilege escalation events
                4. Suspicious network activity
                5. Security recommendations
                
                Focus on potential security threats and compliance issues.
                """,
                
                "performance": f"""
                Analyze the following system logs for performance-related insights:
                
                {log_text}
                
                Please identify:
                1. Resource usage patterns
                2. Performance bottlenecks
                3. Service response times
                4. System load indicators
                5. Performance optimization suggestions
                
                Focus on system efficiency and optimization opportunities.
                """
            }
            
            prompt = prompts.get(analysis_type, prompts["summary"])
            
            # Try Ollama first
            if self.llm_mode == "ollama":
                analysis_text = self._query_ollama(prompt)
                if analysis_text:
                    return {
                        "analysis_type": analysis_type,
                        "logs_analyzed": len(logs),
                        "analysis": analysis_text,
                        "generated_at": datetime.now().isoformat(),
                        "model": f"ollama/{self.ollama_model}",
                        "llm_mode": "ollama"
                    }
                else:
                    # Ollama failed, try Gemini if available
                    logger.warning("Ollama failed, trying Gemini fallback")
                    if self.gemini_api_key and self.model:
                        self.llm_mode = "gemini"
            
            # Use Gemini
            if self.llm_mode == "gemini":
                response = self.model.generate_content(prompt)
                return {
                    "analysis_type": analysis_type,
                    "logs_analyzed": len(logs),
                    "analysis": response.text,
                    "generated_at": datetime.now().isoformat(),
                    "model": "gemini-1.5-flash",
                    "llm_mode": "gemini"
                }
            
            # If both failed, use mock
            return self._mock_analyze_logs(logs, analysis_type)
            
        except Exception as e:
            logger.error(f"Error in log analysis: {e}")
            # Fallback to mock mode on error
            return self._mock_analyze_logs(logs, analysis_type)
    
    def _mock_analyze_logs(self, logs: List[str], analysis_type: str) -> Dict[str, Any]:
        """Mock log analysis for demonstration purposes."""
        
        # Simple pattern detection for mock analysis
        error_patterns = ["error", "failed", "exception", "critical", "alert"]
        warning_patterns = ["warn", "warning", "deprecated", "timeout"]
        security_patterns = ["auth", "login", "sudo", "ssh", "permission", "denied"]
        
        error_count = sum(1 for log in logs if any(pattern in log.lower() for pattern in error_patterns))
        warning_count = sum(1 for log in logs if any(pattern in log.lower() for pattern in warning_patterns))
        security_events = sum(1 for log in logs if any(pattern in log.lower() for pattern in security_patterns))
        
        mock_analyses = {
            "summary": f"""
            SYSTEM LOG ANALYSIS SUMMARY (Mock Mode)
            ========================================
            
            📊 OVERVIEW:
            - Total log entries analyzed: {len(logs)}
            - Potential errors detected: {error_count}
            - Warning messages found: {warning_count}
            - Security-related events: {security_events}
            
            🔍 KEY FINDINGS:
            - System appears to be running normally
            - Regular system maintenance activities detected
            - Service status checks are functioning properly
            - No critical system failures identified
            
            ⚠️ ATTENTION ITEMS:
            {"- Several error messages detected - review recommended" if error_count > 0 else "- No significant issues detected"}
            {"- Multiple warnings found - monitoring suggested" if warning_count > 5 else "- Warning levels are within normal range"}
            
            💡 RECOMMENDATIONS:
            - Continue regular log monitoring
            - Consider log rotation if files are growing large
            - Review any persistent error patterns
            - Ensure backup systems are functioning
            
            Note: This is a mock analysis. For real AI insights, configure Gemini API key.
            """,
            
            "errors": f"""
            ERROR ANALYSIS REPORT (Mock Mode)
            =================================
            
            🚨 CRITICAL ERRORS: {max(0, error_count - 2)}
            - Priority: HIGH
            - Requires immediate attention
            
            ⚠️ WARNINGS: {warning_count}
            - Priority: MEDIUM
            - Monitor for patterns
            
            📋 ERROR BREAKDOWN:
            {"- Multiple error patterns detected in logs" if error_count > 0 else "- No significant errors detected"}
            - System services appear stable
            - No service failures reported
            
            🔧 RECOMMENDED ACTIONS:
            1. Review error logs for specific failure details
            2. Check system resource availability
            3. Verify service configurations
            4. Monitor system performance metrics
            
            Note: This is a mock analysis. Configure Gemini API for detailed insights.
            """,
            
            "security": f"""
            SECURITY ANALYSIS REPORT (Mock Mode)
            ====================================
            
            🔐 AUTHENTICATION EVENTS: {security_events}
            - Login attempts detected
            - Session management active
            
            🛡️ SECURITY STATUS:
            - No unauthorized access attempts detected
            - System access controls functioning
            - Regular authentication activity observed
            
            📊 SECURITY METRICS:
            - Failed login attempts: Within normal range
            - Privilege escalation events: None detected
            - Suspicious network activity: None identified
            
            🚨 SECURITY RECOMMENDATIONS:
            1. Continue monitoring authentication logs
            2. Ensure strong password policies
            3. Review user access permissions regularly
            4. Consider implementing additional monitoring
            
            Note: This is a mock analysis. Configure Gemini API for advanced security insights.
            """,
            
            "performance": f"""
            PERFORMANCE ANALYSIS REPORT (Mock Mode)
            ======================================
            
            📈 PERFORMANCE OVERVIEW:
            - System load appears normal
            - Service response times within acceptable range
            - Resource utilization stable
            
            🔄 RESOURCE USAGE:
            - CPU: Normal activity patterns detected
            - Memory: Usage levels appear stable
            - Disk I/O: Regular read/write operations
            - Network: Standard traffic patterns
            
            ⚡ PERFORMANCE INSIGHTS:
            - No significant performance bottlenecks identified
            - System responsiveness appears adequate
            - Regular maintenance activities observed
            
            💡 OPTIMIZATION SUGGESTIONS:
            1. Monitor disk space usage trends
            2. Review memory usage patterns
            3. Consider log cleanup procedures
            4. Implement performance baseline monitoring
            
            Note: This is a mock analysis. Configure Gemini API for detailed performance insights.
            """
        }
        
        return {
            "analysis_type": analysis_type,
            "logs_analyzed": len(logs),
            "analysis": mock_analyses.get(analysis_type, mock_analyses["summary"]),
            "generated_at": datetime.now().isoformat(),
            "model": "mock-analyzer",
            "mock_mode": True,
            "patterns_detected": {
                "errors": error_count,
                "warnings": warning_count,
                "security_events": security_events
            }
        }
    
    def analyze_system_health(self, system_info: Dict[str, Any], logs: List[str]) -> Dict[str, Any]:
        """Comprehensive system health analysis combining metrics and logs."""
        try:
            if self.llm_mode == "mock":
                return self._mock_health_analysis(system_info, logs)
            
            # Prepare comprehensive analysis prompt
            prompt = f"""
            Analyze the following system information and logs for overall health assessment:
            
            SYSTEM METRICS:
            {system_info}
            
            RECENT LOGS:
            {chr(10).join(logs[-50:])}
            
            Please provide a comprehensive health assessment including:
            1. Overall system health score (1-10)
            2. Critical issues requiring immediate attention
            3. Performance trends and concerns
            4. Security posture assessment
            5. Specific recommendations for improvement
            6. Predicted maintenance needs
            
            Format as a structured health report.
            """
            
            # Try Ollama first
            if self.llm_mode == "ollama":
                analysis_text = self._query_ollama(prompt)
                if analysis_text:
                    return {
                        "health_analysis": analysis_text,
                        "system_info_analyzed": True,
                        "logs_analyzed": len(logs),
                        "generated_at": datetime.now().isoformat(),
                        "model": f"ollama/{self.ollama_model}",
                        "llm_mode": "ollama"
                    }
                else:
                    logger.warning("Ollama failed for health analysis, trying Gemini")
                    if self.gemini_api_key and self.model:
                        self.llm_mode = "gemini"
            
            # Use Gemini
            if self.llm_mode == "gemini":
                response = self.model.generate_content(prompt)
                return {
                    "health_analysis": response.text,
                    "system_info_analyzed": True,
                    "logs_analyzed": len(logs),
                    "generated_at": datetime.now().isoformat(),
                    "model": "gemini-1.5-flash",
                    "llm_mode": "gemini"
                }
            
            # Fallback to mock
            return self._mock_health_analysis(system_info, logs)
            
        except Exception as e:
            logger.error(f"Error in health analysis: {e}")
            return self._mock_health_analysis(system_info, logs)
    
    def _mock_health_analysis(self, system_info: Dict[str, Any], logs: List[str]) -> Dict[str, Any]:
        """Mock health analysis based on system metrics."""
        
        # Extract key metrics for scoring
        cpu_percent = system_info.get("cpu_percent", 0)
        memory_percent = system_info.get("memory", {}).get("percent", 0)
        disk_percent = system_info.get("disk", {}).get("percent", 0)
        
        # Calculate health score
        health_score = 10
        if cpu_percent > 80:
            health_score -= 2
        elif cpu_percent > 60:
            health_score -= 1
            
        if memory_percent > 85:
            health_score -= 2
        elif memory_percent > 70:
            health_score -= 1
            
        if disk_percent > 90:
            health_score -= 3
        elif disk_percent > 80:
            health_score -= 1
        
        health_score = max(1, health_score)
        
        return {
            "health_analysis": f"""
            COMPREHENSIVE SYSTEM HEALTH REPORT (Mock Mode)
            =============================================
            
            🏥 OVERALL HEALTH SCORE: {health_score}/10
            
            📊 SYSTEM METRICS ASSESSMENT:
            - CPU Usage: {cpu_percent:.1f}% {"(HIGH)" if cpu_percent > 70 else "(NORMAL)"}
            - Memory Usage: {memory_percent:.1f}% {"(HIGH)" if memory_percent > 80 else "(NORMAL)"}
            - Disk Usage: {disk_percent:.1f}% {"(HIGH)" if disk_percent > 85 else "(NORMAL)"}
            
            🚨 CRITICAL ISSUES:
            {f"- High CPU usage detected ({cpu_percent:.1f}%)" if cpu_percent > 80 else "- No critical CPU issues"}
            {f"- Memory usage is high ({memory_percent:.1f}%)" if memory_percent > 85 else "- Memory usage within normal range"}
            {f"- Disk space is critically low ({disk_percent:.1f}%)" if disk_percent > 90 else "- Disk space adequate"}
            
            📈 PERFORMANCE TRENDS:
            - System uptime: {system_info.get("uptime", "Unknown")}
            - Boot time: {system_info.get("boot_time", "Unknown")}
            - Overall stability: Good
            
            🔒 SECURITY POSTURE:
            - System access controls: Active
            - Authentication monitoring: Functional
            - Log integrity: Maintained
            
            💡 RECOMMENDATIONS:
            {"1. Investigate high CPU usage causes" if cpu_percent > 70 else "1. CPU performance is optimal"}
            {"2. Review memory-intensive processes" if memory_percent > 70 else "2. Memory usage is healthy"}
            {"3. Clean up disk space immediately" if disk_percent > 85 else "3. Disk space management is good"}
            4. Continue regular monitoring
            5. Maintain current backup procedures
            
            🔮 PREDICTED MAINTENANCE:
            - Next recommended check: 24 hours
            - Log rotation: {"Immediate" if len(logs) > 1000 else "Weekly"}
            - System updates: Check weekly
            
            Note: This is a mock analysis. Configure Gemini API for AI-powered insights.
            """,
            "health_score": health_score,
            "critical_issues": health_score < 7,
            "system_info_analyzed": True,
            "logs_analyzed": len(logs),
            "generated_at": datetime.now().isoformat(),
            "model": "mock-analyzer",
            "mock_mode": True
        }

