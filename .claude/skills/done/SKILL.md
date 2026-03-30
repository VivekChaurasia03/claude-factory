---
name: done
description: Mark current chunk complete and save engineer's field notes to the notes folder.
---

The user has finished chunk $ARGUMENTS.

Do these three things in order:

**1. Write notes/$ARGUMENTS.md** with this structure (keep under 30 lines):

```
# Chunk $ARGUMENTS — [title]

## What this is
One sentence. No fluff.

## Where it lives in the pipeline
One sentence connecting it to Stage 3, Stage 5, or the broader WindBorne stack.

## The production constraint that matters
The one thing that will bite you if you forget it.

## What we built
What the exercise was and what it demonstrated.

## What breaks if you get this wrong
Concrete downstream consequence — not "things go wrong", but specifically what fails.

## Remember this
One sharp takeaway. The kind of thing you'd write on a sticky note.
```

**2. Update LEARN.md and/or WINDBORNE.md** with any new concepts covered in this chunk:
- If the concept is general (Kafka, ClickHouse, Protobuf, NetCDF, backfill patterns) → append to LEARN.md under the relevant section, or create a new section if one doesn't exist.
- If the concept is WindBorne-specific (pipeline shape, QC checks, WeatherMesh constraints, customer types) → append to WINDBORNE.md under the relevant section.
- Only add what's new — do not duplicate what's already there.

**3. Say:** "Filed. What's next?"
