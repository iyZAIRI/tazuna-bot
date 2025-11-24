# Support Card Event Skills Analysis

## Problem
Support card events (like "Forms of Aspiration" for Special Week) can provide skill hints that are not currently shown in our implementation. For example, the "Forms of Aspiration" event can give either Hydrate (201352) or Gourmand (201351) as skill hints.

## What We Found

### Event Data Exists
- Event stories are in `single_mode_story_data` table
- Example: "Forms of Aspiration" (story_id 830025003) for support_card_id 30025
- Event titles are in text_data category 181

### Current Implementation
- Shows hint skills from `single_mode_hint_gain` table
- Query: `WHERE hint_id = ? AND support_card_id = ? AND hint_gain_type = 0`
- This gives us the "guaranteed" hint skills for a support card

### Missing Data
- Event-specific skill rewards (like Gourmand 201351) are NOT in the database
- Searched extensively through all single_mode tables
- Skill 201351 does not appear in any reward or event table

## Possible Explanations

1. **Story Script Files**: Event rewards might be defined in external story script files, not the database
2. **Client-Side Logic**: Game client may determine event rewards dynamically
3. **Hardcoded**: Event skill rewards might be hardcoded in game code
4. **Different Format**: Data might exist in a format we haven't discovered yet

## Tables Checked
- `single_mode_hint_gain` - Only has fixed hint skills
- `single_mode_event_choice_reward` - Only has effect_value_type codes, no skill IDs
- `single_mode_event_item_detail` - No skill IDs found
- `single_mode_reward_set` - No skill IDs in skill range
- `available_skill_set` - For character cards, not support cards

## Current Status
Our implementation shows hint skills from `single_mode_hint_gain`, which provides the core/guaranteed skills for each support card. Event-based skills are not shown.

## Future Work
- May need to examine story script files outside the database
- Could add manual mapping of known event skills
- Add note in UI that event skills aren't included
