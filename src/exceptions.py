class MemberProcessingError(Exception):
    """Exception raised when a member processing fails."""
    
    def __init__(self, member_id, message="Customer member processing failed"):
        # Initialize with the member ID and custom message
        self.member_id = member_id
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        # Customize the string representation to include member_id and message
        return f"Member ID: {self.member_id} - {self.message}"