import asyncio
import logging
from jmflashcards.errors import JMFCError
from jmflashcards.parser import Repository 
from jmflashcards.fcdeluxe import FCDRepository 

logger = logging.getLogger(__name__)


class Syncronizer(object):
    fcd_repository_class = FCDRepository
    repository_class = Repository

    def __init__(self, output_dir,  directory, question_keys, answer_keys,
            empty=True):
        self.output_dir = output_dir
        self.directory = directory
        self.question_keys = question_keys
        self.answer_keys = answer_keys
        self.repository = self.repository_class(directory, self)
        self.fcd_repository = self.fcd_repository_class(output_dir)
        self.empty = empty

    def get_flashcards_status(self):
        fcd_references = set(self.fcd_repository.references())
        logger.debug("fcd_references: %s" % ", ".join(fcd_references))
        references = set(self.repository.references())
        logger.debug("orig_references: %s" % ", ".join(references))
        to_delete = fcd_references.difference(references)
        logger.debug("delete_references: %s" % ", ".join(to_delete))
        new = references.difference(fcd_references)
        logger.debug("new_references: %s" % ", ".join(new))
        common = fcd_references.intersection(references)
        updated = [ x for x in self._iter_updated(common) ]
        logger.debug("Sync running to update:%s    to create:%s    to delete:%s" % ("\n".join(updated), "\n".join(new), "\n".join(to_delete)))
        return updated, list(new), list(to_delete)

    def _iter_updated(self, common):
        for ref in common:
            flashcard = self.repository[ref]
            fcd_flashcard = self.fcd_repository[ref]
            if fcd_flashcard.get_date() < flashcard.get_date():
                yield ref

    def sync(self):
        updated, new, to_delete = self.get_flashcards_status()
        if updated or new:
            print("Starting syncronization")
            if new: print ("New: %d" % len(new))
            if updated: print ("Updating: %d" % len(updated))
            asyncio.run(self.sync2(new+updated))
        elif to_delete:
            print ("Removing: %d" % len(to_delete))
            for fc in to_delete:
                self.delete_flashcard(fc)
        else:
            print("New: %d" % len(new))
            print("Updating: %d" % len(updated))
            print("Removing: %d" % len(to_delete))
            print("Nothing to be done")

    async def sync2(self, coroutines):
        tasks = []
        for fc in coroutines:
            task = asyncio.create_task(self.render_flashcard(fc))
            tasks.append(task)
        await asyncio.gather(*tasks)

    async def render_flashcard(self, ref):
        logger.info("Building flashcard '%s'" % ref)
        if self.empty:
            return
        flashcard = self.repository[ref]
        try:
            flashcard.parse()
            await self.fcd_repository.renderer.render(flashcard)
        except JMFCError as e:
            logger.error(str(e))

    def delete_flashcard(self, ref):
        logger.info("Removing flashcard '%s'" % ref)
        if not self.empty:
            fcd_flashcard = self.fcd_repository[ref]
            fcd_flashcard.delete()












          
