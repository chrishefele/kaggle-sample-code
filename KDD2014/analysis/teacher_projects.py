from collections import defaultdict

project_count = defaultdict(int)

fin = open('../download/projects.csv')
fin.readline() # bypass header

for line in fin:
    tokens = line.split(',')
    projectid = tokens[0]
    teacherid = tokens[1]
    project_count[teacherid] += 1

counts = ((proj_count, teacher_id) for teacher_id, proj_count in project_count.iteritems())
for project_count, teacher_id in sorted(counts, reverse=True):
    print teacher_id, ",", project_count


#projectid,teacher_acctid,schoolid,school_ncesid,school_latitude,school_longitude,school_city,school_state,school_zip,school_metro,school_district,school_county,school_charter,school_magnet,school_year_round,school_nlns,school_kipp,school_charter_ready_promise,teacher_prefix,teacher_teach_for_america,teacher_ny_teaching_fellow,primary_focus_subject,primary_focus_area,secondary_focus_subject,secondary_focus_area,resource_type,poverty_level,grade_level,fulfillment_labor_materials,total_price_excluding_optional_support,total_price_including_optional_support,students_reached,eligible_double_your_impact_match,eligible_almost_home_match,date_posted
