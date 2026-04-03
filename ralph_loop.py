"""
Ralph Loop - AI Employee Vault

"Me fail English? That's unpossible!"

A persistent task processor that keeps working on a task until it's complete.
Implements the Ralph Wiggum "keep working until done" loop with:
- Claude Code support (preferred for hackathon)
- Qwen CLI fallback
- File-based completion detection
- Exponential backoff retry
- Proper stop hook pattern

Usage:
    python ralph_loop.py "Your task description here"
    python ralph_loop.py "Process all files in Needs_Action" --engine claude
    python ralph_loop.py "Update Dashboard" --engine qwen --max-iterations 5

Environment Variables:
    RALPH_ENGINE: "claude" or "qwen" (default: claude)
    RALPH_MAX_ITERATIONS: Max retry count (default: 10)
    RALPH_CHECK_INTERVAL: Seconds between checks (default: 2)
"""

import os
import sys
import time
import re
import subprocess
from datetime import datetime
from pathlib import Path


# Paths
VAULT_PATH = Path(__file__).parent
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
DONE_FOLDER = VAULT_PATH / "Done"
IN_PROGRESS = VAULT_PATH / "In_Progress"

# Configuration from environment
ENGINE = os.getenv('RALPH_ENGINE', 'claude').lower()
MAX_ITERATIONS = int(os.getenv('RALPH_MAX_ITERATIONS', '10'))
CHECK_INTERVAL = int(os.getenv('RALPH_CHECK_INTERVAL', '2'))

# Ensure folders exist
for folder in [NEEDS_ACTION, DONE_FOLDER, IN_PROGRESS]:
    folder.mkdir(parents=True, exist_ok=True)


def create_task_file(task_description: str) -> Path:
    """Create a task file in Needs_Action folder."""
    
    # Generate safe filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_desc = re.sub(r'[^\w\s-]', '', task_description[:30]).strip().replace(' ', '_')
    filename = f"RALPH_TASK_{safe_desc}_{timestamp}.md"
    filepath = NEEDS_ACTION / filename
    
    content = f"""---
type: ralph_task
description: {task_description}
created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
status: pending
iteration: 0
max_iterations: {MAX_ITERATIONS}
---

# Ralph Loop Task

## Task Description
{task_description}

## Instructions
Process this task completely. Do all required actions:
- Read and understand the task
- Execute necessary operations
- Update relevant files (Dashboard.md, etc.)
- Move this file to Done/ folder when complete

## Status Tracking
- Status: PENDING
- Iteration: 0/{MAX_ITERATIONS}
- Started: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Notes
This task is being processed by Ralph Loop.
Keep working until the task is fully complete!

---
*Ralph says: "Me fail English? That's unpossible!"*
"""
    
    filepath.write_text(content, encoding='utf-8')
    print(f"📝 Task file created: {filename}")
    
    return filepath


def run_ai_engine(task_file: Path, iteration: int, engine: str = 'claude') -> bool:
    """Run AI engine (Claude Code or Qwen CLI) to process the task file."""

    engine_name = engine.title()
    print(f"\n🤖 Running {engine_name} (Iteration {iteration}/{MAX_ITERATIONS})...")

    try:
        prompt = f"""Read the task file: {task_file.name} in Needs_Action folder.

IMPORTANT INSTRUCTIONS:
1. Read the task description carefully
2. Process the task completely - do ALL required actions
3. Update any relevant files (Dashboard.md, reports, etc.)
4. When the task is 100% complete, move the task file to Done/ folder
5. Do NOT leave the file in Needs_Action/ if the task is done
6. Output <promise>TASK_COMPLETE</promise> when finished

Task: Process {task_file.name} completely and move to Done/ folder when finished.
"""

        # Choose engine
        if engine == 'claude':
            cmd = ['claude', '-y', '--print', prompt]
            timeout = 600  # 10 minutes for Claude
        else:
            cmd = ['qwen', '-y', prompt]
            timeout = 180  # 3 minutes for Qwen

        result = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=str(VAULT_PATH),
            shell=True,
            timeout=timeout
        )

        print(f"   {engine_name} exit code: {result.returncode}")

        # Check for completion promise
        if '<promise>TASK_COMPLETE</promise>' in result.stdout:
            print(f"   ✅ Task completion promise detected!")
            return True

        if result.stdout:
            output = result.stdout.strip()
            if output:
                print(f"   Output preview: {output[:200]}...")

        if result.stderr:
            errors = result.stderr.strip()
            if errors:
                print(f"   Errors: {errors[:200]}...")

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print(f"   ⚠️  {engine_name} timeout ({timeout//60} min limit)")
        return False
    except FileNotFoundError:
        print(f"   ❌ {engine_name} CLI not found - check installation")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def check_task_status(task_file: Path) -> tuple:
    """Check if task file is in Done folder or still in Needs_Action."""
    
    # Check if file moved to Done folder
    done_filepath = DONE_FOLDER / task_file.name
    if done_filepath.exists():
        return True, "done", done_filepath
    
    # Check if still in Needs_Action
    if task_file.exists():
        # Read the file to check status
        try:
            content = task_file.read_text(encoding='utf-8')
            status_match = re.search(r'status:\s*(\w+)', content)
            status = status_match.group(1) if status_match else 'unknown'
            
            # Check iteration count
            iter_match = re.search(r'iteration:\s*(\d+)', content)
            iteration = int(iter_match.group(1)) if iter_match else 0
            
            return False, status, task_file
        except:
            return False, 'unknown', task_file
    
    # File not found anywhere - might have been moved with different name
    # Search for similar files in Done folder
    for done_file in DONE_FOLDER.glob('*.md'):
        try:
            content = done_file.read_text(encoding='utf-8')
            if task_file.stem in content or 'ralph_task' in content.lower():
                return True, 'done', done_file
        except:
            continue
    
    return False, 'missing', None


def update_task_iteration(task_file: Path, iteration: int):
    """Update the iteration count in the task file."""
    
    if not task_file.exists():
        return
    
    try:
        content = task_file.read_text(encoding='utf-8')
        
        # Update iteration count
        content = re.sub(
            r'iteration:\s*\d+',
            f'iteration: {iteration}',
            content
        )
        
        # Update status tracking section
        content = re.sub(
            r'- Iteration: \d+/',
            f'- Iteration: {iteration}/',
            content
        )
        
        task_file.write_text(content, encoding='utf-8')
    except Exception as e:
        print(f"   ⚠️  Could not update iteration: {e}")


def print_ralph_quote(iteration: int):
    """Print a random Ralph Wiggum quote for motivation."""
    
    quotes = [
        "Me fail English? That's unpossible!",
        "I'm in a pickle!",
        "My cat's breath smells like cat food.",
        "I want to share something with you: Three can keep a secret, if two of them are dead.",
        "Lamb... Lamb... Lamb...",
        "The teacher said to start at page 1, so I did!",
        "I'm not a bad guy! I work hard, and I love my kids. So why should I be singled out?",
        "But I don't WANT to go on the celibacy diet!",
    ]
    
    quote_index = iteration % len(quotes)
    print(f"\n💬 Ralph says: \"{quotes[quote_index]}\"")


def main():
    """Main function to run Ralph Loop."""

    print("=" * 70)
    print("🔁 RALPH LOOP - Persistent Task Processor")
    print("=" * 70)
    print("\n\"Me fail English? That's unpossible!\"")
    print("\nThis script will keep running AI engine until the task is complete.")
    print(f"Engine: {ENGINE.title()}")
    print(f"Maximum iterations: {MAX_ITERATIONS}")
    print("=" * 70)

    # Check for task description argument
    if len(sys.argv) < 2:
        print("\n❌ Error: No task description provided!")
        print("\nUsage:")
        print('  python ralph_loop.py "Your task description here"')
        print('  python ralph_loop.py "Task" --engine claude --max-iterations 5')
        print("\nExample:")
        print('  python ralph_loop.py "Update Dashboard.md with latest sales data"')
        sys.exit(1)

    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('task', nargs='+', help='Task description')
    parser.add_argument('--engine', choices=['claude', 'qwen'], default=ENGINE, help='AI engine to use')
    parser.add_argument('--max-iterations', type=int, default=MAX_ITERATIONS, help='Max iterations')
    args = parser.parse_args()

    task_description = " ".join(args.task)
    engine = args.engine
    max_iterations = args.max_iterations

    print(f"\n📋 Task: {task_description}")
    print(f"🔧 Engine: {engine.title()}")
    print(f"🔄 Max iterations: {max_iterations}")

    # Create task file
    print("\n📝 Creating task file...")
    task_file = create_task_file(task_description)

    print("\n" + "=" * 70)
    print("🔄 STARTING RALPH LOOP")
    print("=" * 70)

    iteration = 1
    task_complete = False
    status = "pending"
    consecutive_failures = 0

    while iteration <= max_iterations and not task_complete:
        print(f"\n{'='*70}")
        print(f"📊 ITERATION {iteration}/{max_iterations}")
        print(f"{'='*70}")

        # Print Ralph quote every 3 iterations for motivation
        if iteration % 3 == 0:
            print_ralph_quote(iteration)

        # Run AI engine to process the task
        success = run_ai_engine(task_file, iteration, engine)

        if not success:
            consecutive_failures += 1
            # Exponential backoff: 2, 4, 8, 16, 32 seconds
            backoff = min(2 ** consecutive_failures, 32)
            print(f"\n⚠️  Consecutive failures: {consecutive_failures}")
            print(f"⏳ Backing off for {backoff} seconds...")
            time.sleep(backoff)
        else:
            consecutive_failures = 0  # Reset on success

        # Wait a moment for file operations to complete
        time.sleep(CHECK_INTERVAL)

        # Check task status
        task_complete, status, location = check_task_status(task_file)

        print(f"\n📈 Status Check:")
        print(f"   Task Complete: {'✅ YES' if task_complete else '❌ NO'}")
        print(f"   Status: {status}")
        print(f"   Location: {location}")

        if task_complete:
            print(f"\n🎉 TASK COMPLETED!")
            print(f"   File moved to: {location}")
            print(f"   Total iterations: {iteration}")
            break

        # Update iteration count in task file
        update_task_iteration(task_file, iteration)

        if iteration < max_iterations:
            print(f"\n⏳ Task not complete. Retrying in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)

        iteration += 1

    # Final status
    print("\n" + "=" * 70)
    print("🏁 RALPH LOOP FINISHED")
    print("=" * 70)

    if task_complete:
        print(f"\n✅ SUCCESS! Task completed in {iteration} iteration(s).")
        print(f"   Final location: {location}")
        print("\n🎊 Ralph is happy!")
    else:
        print(f"\n⚠️  MAX ITERATIONS REACHED ({max_iterations})")
        print(f"   Task may still be in progress or stuck.")
        print(f"   Current status: {status}")
        print(f"   Check Needs_Action/ folder for the task file.")
        print("\n💡 Suggestions:")
        print("   1. Check the task file for errors")
        print("   2. Run AI engine manually with more specific instructions")
        print("   3. Break the task into smaller subtasks")
        print("   4. Try switching engine (--engine claude or --engine qwen)")

    print("\n" + "=" * 70)
    print(f"Final iteration count: {iteration - 1 if task_complete else max_iterations}")
    print(f"Task status: {status.upper()}")
    print(f"Consecutive failures at end: {consecutive_failures}")
    print("=" * 70)

    # Return appropriate exit code
    sys.exit(0 if task_complete else 1)


if __name__ == "__main__":
    main()
