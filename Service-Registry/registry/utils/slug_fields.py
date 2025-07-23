import os
import uuid


class BaseSlug:
    """ Abstract Class for Generating Slug from a Object. """
    @classmethod
    def get_slug(cls, instance):
        """ Abstract method to get slug from object. """
        raise NotImplementedError("Subclass needs to implement this get_slug method.")
    
    @classmethod
    def slug_method(cls, value):
        """ Abstract method to slugify the instance from object. """
        raise NotImplementedError("The Slug method for abstract class can not be implemented.")
    
    
class UserSlug(BaseSlug):
    """ Class for Generating Slug from a User Object. """
    @classmethod
    def get_slug(cls, instance):
        """ Method to get slug from user object. """
        return f"{instance.first_name}-{instance.last_name}"
    
    @classmethod
    def slug_method(cls, value):
        """ Method to get slug from user object. """
        return value.replace(' ', '-').lower()
    
    
class MediaSlug(BaseSlug):
    """ Class for Generating Slug from a Media Object. """

    @classmethod
    def get_slug(cls, instance):
        """ Method to get slug from media object. """
        # Generate slug (unchanged)
        if not instance.slug and instance.original_filename:
            return os.path.splitext(instance.original_filename)[0]
        return instance.title
    
    @classmethod
    def slug_method(cls, value):
        """ Slug function to generate slug from string. """
        return value.replace(' ', '-').lower()
    
class CourseSlug(BaseSlug):
    """ Class for Generating Slug from a Course Object. """

    @classmethod
    def get_slug(cls, instance):
        """ Method to get slug from Course object. """
        # Generate slug (unchanged)
        if not instance.slug and instance.level:
            return f"{instance.category.name}-{instance.level}-{instance.title}"
        return f"{instance.category.name}-{instance.title}"     
    
    @classmethod
    def slug_method(cls, value):
        """ Slug function to generate slug from string. """
        return value.replace(' ', '-').lower()
    
class CategorySlug(BaseSlug):
    """ Class for Generating Slug from a Course Object. """

    @classmethod
    def get_slug(cls, instance):
        """ Method to get slug from Course object. """
        # Generate slug (unchanged)
        return instance.name
    
    @classmethod
    def slug_method(cls, value):
        """ Slug function to generate slug from string. """
        return value.replace(' ', '-').lower()
    
class ModuleSlug(BaseSlug):
    """ Class for Generating Slug from a Module Object. """

    @classmethod
    def get_slug(cls, instance):
        """ Method to get slug from Module object. """
        # Generate slug (unchanged)
        return f"module-{instance.title}-{uuid.uuid4()}"
    
    @classmethod
    def slug_method(cls, value):
        """ Slug function to generate slug from string. """
        return value.replace(' ', '-').lower()
    
class LessonSlug(BaseSlug):
    """ Class for Generating Slug from a Lesson Object. """

    @classmethod
    def get_slug(cls, instance):
        """ Method to get slug from Lesson object. """
        # Generate slug (unchanged)
        return f"module-{instance.title}-{uuid.uuid4()}"
    
    @classmethod
    def slug_method(cls, value):
        """ Slug function to generate slug from string. """
        return value.replace(' ', '-').lower()
    
    
        
