# 📋 Service Level Agreement (SLA)

**Version:** 1.0  
**Effective Date:** January 1, 2024  
**Last Updated:** November 2024

---

## 1. Overview

This Service Level Agreement ("SLA") describes the uptime and performance commitments for the Background Removal API ("Service"). This SLA applies to paid subscription plans.

---

## 2. Uptime Commitments

### 2.1 Monthly Uptime Percentage

| Plan | Uptime Guarantee | Service Credits |
|------|------------------|-----------------|
| Free | Best Effort | None |
| Basic | 99.0% | 10% credit if below |
| Pro | 99.5% | 25% credit if below |
| Enterprise | 99.9% | 50% credit if below |

### 2.2 Uptime Calculation

**Monthly Uptime Percentage** = (Total Minutes in Month - Downtime Minutes) / Total Minutes in Month × 100

**Example:**
- Month: 30 days = 43,200 minutes
- Downtime: 43 minutes
- Uptime: (43,200 - 43) / 43,200 × 100 = 99.90%

### 2.3 Excluded Downtime

The following are NOT counted as downtime:
- Scheduled maintenance (with 48-hour notice)
- Downtime caused by third-party services (Replicate.com)
- Issues caused by customer's infrastructure
- Force majeure events
- Customer's violation of Terms of Service
- DDoS attacks or malicious activity
- Beta/preview features

---

## 3. Performance Targets

### 3.1 Response Times

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response (p50) | < 2 seconds | Median response time |
| API Response (p95) | < 5 seconds | 95th percentile |
| API Response (p99) | < 10 seconds | 99th percentile |

**Note:** Response times exclude AI processing time, which varies based on:
- Image size and resolution
- Image complexity
- Current system load
- Replicate.com processing time

**Typical AI Processing Time:** 2-10 seconds per image

### 3.2 Rate Limits

| Plan | Rate Limit | Burst Allowance |
|------|-----------|-----------------|
| Free | 50/day | 5/minute |
| Basic | 1,000/day | 20/minute |
| Pro | 10,000/day | 100/minute |
| Enterprise | Custom | Custom |

---

## 4. Support Response Times

### 4.1 Support Channels

| Plan | Channels | Response Time | Resolution Time |
|------|----------|---------------|-----------------|
| Free | Community Forum | Best Effort | Best Effort |
| Basic | Email | 48 hours | 5 business days |
| Pro | Priority Email | 24 hours | 3 business days |
| Enterprise | 24/7 Phone & Email | 4 hours | 1 business day |

### 4.2 Severity Levels

**Critical (P1):**
- Service completely unavailable
- Data loss or corruption
- Security breach

**High (P2):**
- Major feature not working
- Performance severely degraded
- Affects multiple users

**Medium (P3):**
- Minor feature not working
- Workaround available
- Affects single user

**Low (P4):**
- General questions
- Feature requests
- Documentation issues

### 4.3 Response Time by Severity

| Severity | Free | Basic | Pro | Enterprise |
|----------|------|-------|-----|------------|
| P1 | N/A | 24h | 8h | 1h |
| P2 | N/A | 48h | 24h | 4h |
| P3 | Best Effort | 72h | 48h | 8h |
| P4 | Best Effort | 5 days | 3 days | 24h |

---

## 5. Scheduled Maintenance

### 5.1 Maintenance Windows

- **Frequency:** Monthly (typically)
- **Duration:** Maximum 2 hours
- **Timing:** Weekends, 2 AM - 4 AM UTC
- **Advance Notice:** 48 hours minimum

### 5.2 Emergency Maintenance

Emergency maintenance may be performed without advance notice for:
- Critical security vulnerabilities
- Data integrity issues
- Service-impacting bugs

**Target Duration:** < 30 minutes

---

## 6. Service Credits

### 6.1 Credit Calculation

| Uptime Achievement | Service Credit |
|-------------------|----------------|
| 99.9% - 99.0% | 10% of monthly fee |
| 99.0% - 95.0% | 25% of monthly fee |
| < 95.0% | 50% of monthly fee |

### 6.2 Maximum Monthly Credit

Maximum service credit per month: **50% of monthly subscription fee**

### 6.3 How to Claim

1. Submit support ticket within **30 days** of incident
2. Include:
   - Dates and times of unavailability
   - Request logs or error messages
   - Impact description
3. Review and approval within **5 business days**
4. Credit applied to **next billing cycle**

### 6.4 Credit Limitations

- Credits cannot be exchanged for cash
- Credits are sole remedy for SLA violations
- Multiple outages in same month are aggregated
- Free plan is not eligible for credits

---

## 7. Monitoring and Status

### 7.1 Status Page

**URL:** status.backgroundremoval.api

Real-time status updates for:
- API availability
- Response times
- Incident reports
- Scheduled maintenance

### 7.2 Incident Notifications

**Pro and Enterprise plans:**
- Email notifications for P1/P2 incidents
- SMS notifications (Enterprise only)
- Webhook notifications (Enterprise only)

### 7.3 Monitoring Systems

- **24/7 automated monitoring**
- Health checks every 60 seconds
- Multiple geographic regions
- Alert escalation procedures

---

## 8. Data and Security

### 8.1 Data Retention

| Data Type | Retention Period |
|-----------|------------------|
| Request logs | 30 days |
| Error logs | 90 days |
| Cached results | 1 hour (configurable) |
| User images | Not stored* |

*Images are processed in real-time and not permanently stored

### 8.2 Backups

- Configuration data: Daily backups
- User settings: Daily backups
- Backup retention: 30 days
- Backup restoration: Within 4 hours

### 8.3 Security Measures

- TLS 1.2+ encryption for all traffic
- API key authentication
- Rate limiting and DDoS protection
- Regular security audits
- SOC 2 Type II compliance (Enterprise)
- Penetration testing (Quarterly)

---

## 9. Disaster Recovery

### 9.1 Recovery Objectives

| Metric | Target |
|--------|--------|
| **RTO** (Recovery Time Objective) | 4 hours |
| **RPO** (Recovery Point Objective) | 24 hours |

### 9.2 Disaster Scenarios

- Regional datacenter failure
- Database corruption
- Critical infrastructure failure
- Natural disasters

### 9.3 Failover

- **Automatic failover:** Yes (Enterprise)
- **Multi-region deployment:** Enterprise only
- **Data replication:** Real-time (Enterprise)

---

## 10. Capacity and Scaling

### 10.1 Capacity Planning

- Continuous monitoring of system capacity
- Automatic scaling based on demand
- Proactive upgrades before capacity limits

### 10.2 Fair Use Policy

While Enterprise plans include "unlimited" requests:
- Must follow fair use guidelines
- Excessive abuse may be throttled
- Notification before any throttling action

**Excessive use examples:**
- > 1 million requests/day without notice
- Automated stress testing
- Scraping or data mining

---

## 11. Compliance and Certifications

### 11.1 Current Compliance

- ✅ GDPR compliant
- ✅ CCPA compliant
- ✅ HTTPS/TLS encryption
- ✅ Regular security audits

### 11.2 Enterprise Compliance

- ✅ SOC 2 Type II (in progress)
- ✅ HIPAA compliance (on request)
- ✅ Custom data processing agreements
- ✅ On-premise deployment options

---

## 12. Reporting and Transparency

### 12.1 Monthly Reports (Enterprise)

- Uptime statistics
- Performance metrics
- Incident summaries
- Usage analytics

### 12.2 Annual Report (Public)

Published yearly:
- Overall uptime statistics
- Major incidents and resolutions
- Infrastructure improvements
- Security updates

---

## 13. SLA Modifications

### 13.1 Changes to SLA

We reserve the right to modify this SLA with:
- **30 days advance notice** for paid plans
- Notification via email and status page
- Continued use constitutes acceptance

### 13.2 Service Improvements

We may improve service levels without notice:
- Increased uptime guarantees
- Faster response times
- Additional features

---

## 14. Termination

### 14.1 By Customer

- Cancel anytime via RapidAPI dashboard
- No early termination fees
- Access continues until end of billing period
- Pro-rated refunds for annual plans

### 14.2 By Provider

We may terminate service for:
- Non-payment
- Terms of Service violations
- Illegal activity
- Excessive abuse

**Notice period:** 30 days (except for violations)

---

## 15. Limitations and Disclaimers

### 15.1 Third-Party Dependencies

This service relies on:
- **Replicate.com** for AI processing
- **Cloud infrastructure providers**
- **CDN services**

Downtime caused by these services is excluded from SLA calculations.

### 15.2 Beta Features

Beta/preview features are provided "as-is" without:
- Uptime guarantees
- Performance targets
- Support SLAs

---

## 16. Contact Information

### 16.1 Support

- **Email:** support@backgroundremoval.api
- **Phone:** +1 (555) 123-4567 (Enterprise)
- **Status Page:** status.backgroundremoval.api
- **Documentation:** docs.backgroundremoval.api

### 16.2 Sales

- **Email:** sales@backgroundremoval.api
- **Phone:** +1 (555) 123-4568
- **Schedule Demo:** calendly.com/your-demo

### 16.3 Security Issues

- **Email:** security@backgroundremoval.api
- **PGP Key:** Available on request
- **Bug Bounty:** security.backgroundremoval.api/bounty

---

## 17. Definitions

**Downtime:** Period when API returns 5xx errors for > 5 consecutive minutes

**Response Time:** Time from request receipt to response transmission (excludes AI processing)

**Business Day:** Monday-Friday, excluding US federal holidays

**Uptime:** Service is accessible and functioning normally

**Incident:** Unplanned service interruption or degradation

**Maintenance:** Planned service interruption with advance notice

---

## 18. Agreement

By using this service, you agree to the terms of this SLA. If you do not agree, discontinue use of the service.

**Questions?** Contact us at legal@backgroundremoval.api

---

*This SLA is effective as of the date listed above and supersedes all prior agreements.*

**Last Review:** November 2024  
**Next Review:** February 2025

