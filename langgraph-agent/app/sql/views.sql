-- ==================================================
-- Asset View
-- ==================================================

CREATE VIEW vw_grc_asset_overview AS
SELECT
    a.id AS asset_id,
    a.name AS asset_name,
    ag.name AS asset_group,
    av.valuation_level_name AS asset_value_level,
    l.name AS location_name,
    a.verified,
    a.created
FROM simplerisk.assets a
LEFT JOIN simplerisk.assets_asset_groups aag
    ON a.id = aag.asset_id
LEFT JOIN simplerisk.asset_groups ag
    ON ag.id = aag.asset_group_id
LEFT JOIN simplerisk.asset_values av
    ON a.value = av.id
LEFT JOIN simplerisk.location l
    ON a.location = l.value;

-- ==================================================
-- Framework Compliance View
-- ==================================================

CREATE VIEW vw_framework_compliance AS
SELECT
    f.value AS framework_id,
    CAST(f.name AS CHAR(255)) AS framework_name,

    fc.id AS control_id,
    fc.control_number,

    CAST(fc.short_name AS CHAR(255)) AS control_name,

    fcm.reference_name,

    fct.id AS test_id,
    CAST(fct.name AS CHAR(255)) AS test_name,

    fctr.test_result,
    fctr.test_date,

    fc.control_maturity,
    fc.desired_maturity

FROM simplerisk.frameworks f

LEFT JOIN simplerisk.framework_control_mappings fcm
    ON f.value = fcm.framework

LEFT JOIN simplerisk.framework_controls fc
    ON fc.id = fcm.control_id

LEFT JOIN simplerisk.framework_control_tests fct
    ON fc.id = fct.framework_control_id

LEFT JOIN simplerisk.framework_control_test_results fctr
    ON fct.id = fctr.test_audit_id;


-- ============================================
-- Control Status View
-- ============================================
CREATE VIEW vw_control_status AS
SELECT
    fc.id AS control_id,
    fc.control_number,
    CAST(fc.short_name AS CHAR(255)) AS control_name,

    fc.control_status,
    fc.control_maturity,
    fc.desired_maturity,

    fct.id AS test_id,
    CAST(fct.name AS CHAR(255)) AS test_name,

    fctr.test_result,
    fctr.test_date

FROM simplerisk.framework_controls fc

LEFT JOIN simplerisk.framework_control_tests fct
       ON fc.id = fct.framework_control_id

LEFT JOIN simplerisk.framework_control_test_results fctr
       ON fct.id = fctr.test_audit_id;

-- ============================================
-- Document View
-- ============================================
CREATE VIEW vw_document_summary AS
SELECT
    d.id AS document_id,
    d.document_name,
    d.document_type,
    d.document_status,
    d.document_owner,
    d.creation_date,
    d.approval_date,
    d.last_review_date,
    d.next_review_date,

    cf.id AS file_id,
    cf.name AS file_name,
    cf.type AS file_type,
    cf.size AS file_size,
    cf.version,
    cf.timestamp AS uploaded_at

FROM simplerisk.documents d

LEFT JOIN simplerisk.compliance_files cf
       ON d.id = cf.ref_id
      AND cf.ref_type = 'documents';

-- ============================================
-- Mitigation View
-- ============================================

CREATE VIEW vw_mitigation_summary AS
SELECT
    m.id AS mitigation_id,
    m.risk_id,

    CAST(r.subject AS CHAR(255)) AS risk_subject,
    r.status AS risk_status,

    m.submission_date,
    m.last_update,
    m.planning_date,

    m.mitigation_percent,
    m.mitigation_cost,
    m.mitigation_effort,

    CAST(m.current_solution AS CHAR(1000)) AS current_solution,
    CAST(m.security_requirements AS CHAR(1000)) AS security_requirements,
    CAST(m.security_recommendations AS CHAR(1000)) AS security_recommendations

FROM simplerisk.mitigations m

LEFT JOIN simplerisk.risks r
       ON m.risk_id = r.id;